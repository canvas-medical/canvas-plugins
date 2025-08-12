import json
import uuid
from datetime import datetime
from http import HTTPStatus

import arrow

from django.db.models import Case, When, Value, Q, CharField

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import Response, JSONResponse, HTMLResponse
from canvas_sdk.effects.task import AddTaskComment, AddTask
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import StaffSessionAuthMixin, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import ImagingOrder, LabOrder, Referral, PracticeLocation
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.v1.data.task import TaskStatus
from logger import log
from canvas_sdk.caching.plugins import get_cache


ROUTINE = "routine"
URGENT = "urgent"


class OrderTrackingApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        return LaunchModalEffect(
            content=render_to_string("templates/worklist_orders.html", context={
                "patientChartApplication": "order_tracking.applications.patient_order_tracking_app:PatientOrderTrackingApplication"}),
            target=LaunchModalEffect.TargetType.PAGE,
        ).apply()


class OrderTrackingApi(StaffSessionAuthMixin, SimpleAPI):

    @api.get("/main.css")
    def get_main_css(self) -> list[Response | Effect]:
        return [
            Response(
                render_to_string("static/main.css").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/css",
            )
        ]

    @api.get("/main.js")
    def get_main_js(self) -> list[Response | Effect]:
        return [
            Response(
                render_to_string("static/main.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]

    def _get_permalink_for_command(self, order: LabOrder | ImagingOrder | Referral, commandType: str) -> str:
        return f"noteId={order.note.dbid}&commandId={order.dbid}&commandType={commandType}"

    def _create_imaging_order_payload(self, imaging_order: ImagingOrder, include_type: bool = False) -> dict:
        """Create standardized payload for imaging order."""
        payload = {
            "id": str(imaging_order.id),
            "patient_name": imaging_order.patient.preferred_full_name,
            "patient_id": str(imaging_order.patient.id),
            "dob": arrow.get(imaging_order.patient.birth_date).format("YYYY-MM-DD"),
            "status": imaging_order.order_status,
            "order": imaging_order.imaging,
            "ordered_date": imaging_order.date_time_ordered.isoformat() if imaging_order.date_time_ordered else None,
            "created_date": imaging_order.created.isoformat() if imaging_order.created else None,
            "priority": imaging_order.priority or ROUTINE,
            "sent_to": imaging_order.imaging_center.full_name_and_specialty if imaging_order.imaging_center else None,
            "permalink": self._get_permalink_for_command(imaging_order, "imagingOrder"),
            "ordering_provider": {
                "preferred_name": imaging_order.ordering_provider.credentialed_name,
                "id": str(imaging_order.ordering_provider.id),
            }
        }
        if include_type:
            payload["type"] = "imaging"
            payload["sort_key"] = imaging_order.created
        return payload

    def _create_lab_order_payload(self, lab_order: LabOrder, include_type: bool = False) -> dict:
        """Create standardized payload for lab order."""
        lab_tests = list(lab_order.tests.values_list("ontology_test_name", flat=True).all())
        payload = {
            "patient_name": lab_order.patient.preferred_full_name,
            "patient_id": str(lab_order.patient.id),
            "dob": arrow.get(lab_order.patient.birth_date).format("YYYY-MM-DD"),
            "status": lab_order.order_status,
            "order": ", ".join(lab_tests),
            "created_date": lab_order.created.isoformat() if lab_order.created else None,
            "ordered_date": lab_order.date_ordered.isoformat() if lab_order.date_ordered else None,
            "sent_to": lab_order.ontology_lab_partner,
            "permalink": self._get_permalink_for_command(lab_order, "labOrder"),
            "priority": ROUTINE,
            "ordering_provider": {
                "preferred_name": lab_order.ordering_provider.credentialed_name,
                "id": str(lab_order.ordering_provider.id),
            }
        }
        if include_type:
            payload["type"] = "lab"
            payload["sort_key"] = lab_order.created
        return payload

    def _create_referral_order_payload(self, referral_order: Referral, include_type: bool = False) -> dict:
        """Create standardized payload for referral order."""

        order = ["Referral"]
        if referral_order.service_provider and referral_order.service_provider.specialty:
            order.append(f"to {referral_order.service_provider.specialty}")

        payload = {
            "id": str(referral_order.id),
            "patient_name": referral_order.patient.preferred_full_name,
            "patient_id": str(referral_order.patient.id),
            "dob": arrow.get(referral_order.patient.birth_date).format("YYYY-MM-DD"),
            "order": " ".join(order),
            "status": referral_order.order_status,
            "created_date": referral_order.created.isoformat() if referral_order.created else None,
            "priority": referral_order.priority or ROUTINE,
            "sent_to": referral_order.service_provider.full_name_and_specialty if referral_order.service_provider else None,
            "permalink": self._get_permalink_for_command(referral_order, "referral"),
            "ordered_date": referral_order.date_referred.isoformat() if referral_order.date_referred else None,
            "ordering_provider": {
                "preferred_name": referral_order.note.provider.credentialed_name,
                "id": str(referral_order.note.provider.id),
            }
        }
        if include_type:
            payload["type"] = "referral"
            payload["sort_key"] = referral_order.created
        return payload

    @api.get("/providers")
    def providers(self) -> list[Response | Effect]:
        logged_in_staff = self.request.headers["canvas-logged-in-user-id"]

        # Get staff with imaging orders and lab orders separately, then combine
        imaging_staff_ids = set(Staff.objects.filter(
            imaging_orders__isnull=False
        ).values_list('id', flat=True).distinct())

        lab_staff_ids = set(Staff.objects.filter(
            lab_orders__isnull=False
        ).values_list('id', flat=True).distinct())

        # Combine the sets to get all staff with either type of order
        all_ordering_staff_ids = imaging_staff_ids | lab_staff_ids

        ordering_providers = [
            {
                "preferred_name": staff.credentialed_name,
                "id": str(staff.id),
            }
            for staff in Staff.objects.filter(id__in=all_ordering_staff_ids)
        ]

        return [JSONResponse({
            "logged_in_staff_id": logged_in_staff,
            "providers": ordering_providers,
        }, status_code=HTTPStatus.OK)]

    @api.get("/locations")
    def locations(self) -> list[Response | Effect]:
        logged_in_staff = self.request.headers["canvas-logged-in-user-id"]

        locations = PracticeLocation.objects.values("id", "full_name").filter(active=True)
        locations = [{ "name": location["full_name"], "value": str(location["id"]) } for location in locations]

        return [JSONResponse({
            "logged_in_staff_id": logged_in_staff,
            "locations": locations,
        }, status_code=HTTPStatus.OK)]

    @api.get("/orders")
    def orders(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"])

        # Get query parameters for filtering and pagination
        provider_ids = self.request.query_params.get("provider_ids")
        if provider_ids:
            provider_ids = provider_ids.split(",")

        patient_id = self.request.query_params.get("patient_id")
        patient_name = self.request.query_params.get("patient_name")
        patient_dob = self.request.query_params.get("patient_dob")
        location_id = self.request.query_params.get("location")
        sent_to = self.request.query_params.get("sent_to")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        status = self.request.query_params.get("status")
        order_types = self.request.query_params.get("types")
        priority = self.request.query_params.get("priority", "all")

        if order_types:
            order_types = [order_type.lower() for order_type in order_types.split(",")]

        page = int(self.request.query_params.get("page", 1))
        page_size = int(self.request.query_params.get("page_size", 20))

        # Build querysets with filters and select_related for efficiency
        # Only show imaging orders that don't have an associated ImagingReport
        imaging_orders_queryset = ImagingOrder.objects.select_related('patient', 'ordering_provider').annotate(
            order_status=Case(
                When(
                    Q(results__isnull=True) & Q(delegated=True),
                    then=Value("delegated"),
                ),
                When(
                    Q(results__isnull=True) & Q(delegated=False),
                    then=Value("open")
                ),
                default=Value("closed"),
                output_field=CharField()
            )
        ).filter(
            deleted=False
        )

        refer_queryset = Referral.objects.select_related('patient', 'note__provider').annotate(
            order_status=Case(
                When(
                    Q(reports__isnull=True) & Q(forwarded=True),
                    then=Value("delegated"),
                ),
                When(
                    Q(reports__isnull=True) & Q(forwarded=False),
                    then=Value("open")
                ),
                default=Value("closed"),
                output_field=CharField()
            )
        ).filter(
           deleted=False
        )

        lab_orders_queryset = LabOrder.objects.select_related('patient', 'ordering_provider').annotate(
            order_status=Case(
                When(
                    Q(healthgorilla_id="") & Q(reports__isnull=True),
                    then=Value("open")
                ),
                default=Value("closed"),
                output_field=CharField()
            )
        ).filter(
            deleted=False,
        )

        # Apply provider filter if specified
        if provider_ids:
            imaging_orders_queryset = imaging_orders_queryset.filter(ordering_provider__id__in=provider_ids)
            lab_orders_queryset = lab_orders_queryset.filter(ordering_provider__id__in=provider_ids)
            refer_queryset = refer_queryset.filter(note__provider__id__in=provider_ids)

        if patient_id:
            imaging_orders_queryset = imaging_orders_queryset.filter(patient__id=patient_id)
            lab_orders_queryset = lab_orders_queryset.filter(patient__id=patient_id)
            refer_queryset = refer_queryset.filter(patient__id=patient_id)

        if location_id:
            imaging_orders_queryset = imaging_orders_queryset.filter(note__location__id=location_id)
            lab_orders_queryset = lab_orders_queryset.filter(note__location__id=location_id)
            refer_queryset = refer_queryset.filter(note__location__id=location_id)

        if status and status != "all":
            imaging_orders_queryset = imaging_orders_queryset.filter(order_status=status)
            refer_queryset = refer_queryset.filter(order_status=status)

            # lab order don't have delegated status
            if status != "delegated":
                lab_orders_queryset = lab_orders_queryset.filter(order_status=status)
        elif not status:
            imaging_orders_queryset = imaging_orders_queryset.exclude(order_status="closed")
            refer_queryset = refer_queryset.exclude(order_status="closed")
            lab_orders_queryset = lab_orders_queryset.exclude(order_status="closed")

        if patient_name and not patient_id:
            name_filter = (
                Q(patient__first_name__icontains=patient_name) |
                Q(patient__last_name__icontains=patient_name)
            )
            imaging_orders_queryset = imaging_orders_queryset.filter(name_filter)
            lab_orders_queryset = lab_orders_queryset.filter(name_filter)
            refer_queryset = refer_queryset.filter(name_filter)

        if patient_dob:
            try:
                dob_date = datetime.strptime(patient_dob, '%Y-%m-%d').date()
                imaging_orders_queryset = imaging_orders_queryset.filter(patient__birth_date=dob_date)
                lab_orders_queryset = lab_orders_queryset.filter(patient__birth_date=dob_date)
                refer_queryset = refer_queryset.filter(patient__birth_date=dob_date)
            except ValueError:
                pass  # Invalid date format, skip filter

        if sent_to:
            imaging_orders_queryset = imaging_orders_queryset.filter(
                Q(imaging_center__first_name__icontains=sent_to)|
                Q(imaging_center__last_name__icontains=sent_to)|
                Q(imaging_center__specialty__icontains=sent_to) |
                Q(imaging_center__practice_name__icontains=sent_to)
            )
            lab_orders_queryset = lab_orders_queryset.filter(
                ontology_lab_partner__icontains=sent_to
            )
            refer_queryset = refer_queryset.filter(
                Q(service_provider__first_name__icontains=sent_to)|
                Q(service_provider__last_name__icontains=sent_to)|
                Q(service_provider__specialty__icontains=sent_to) |
                Q(service_provider__practice_name__icontains=sent_to)
            )

        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                imaging_orders_queryset = imaging_orders_queryset.filter(date_time_ordered__gte=from_date)
                lab_orders_queryset = lab_orders_queryset.filter(date_ordered__gte=from_date)
                refer_queryset = refer_queryset.filter(date_referred__gte=from_date)
            except ValueError:
                pass

        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                imaging_orders_queryset = imaging_orders_queryset.filter(date_time_ordered__lte=to_date)
                lab_orders_queryset = lab_orders_queryset.filter(date_ordered__lte=to_date)
                refer_queryset = refer_queryset.filter(date_referred__lte=to_date)
            except ValueError:
                pass

        if priority == 'urgent':
            # Filter for urgent orders only
            imaging_orders_queryset = imaging_orders_queryset.filter(priority="Urgent")
            refer_queryset = refer_queryset.filter(priority="Urgent")
            # Lab orders don't have a priority, so exclude them for urgent
            lab_orders_queryset = lab_orders_queryset.none()  # Empty queryset
        elif priority == 'routine':
            # Filter for routine orders
            imaging_orders_queryset = imaging_orders_queryset.exclude(priority="Urgent")
            refer_queryset = refer_queryset.exclude(priority="Urgent")
            # Lab orders are always routine (keep as is)

        # Apply ordering for consistent results
        imaging_orders_queryset = imaging_orders_queryset.order_by('-created')
        lab_orders_queryset = lab_orders_queryset.order_by('-created', "id").distinct("id", "created")
        refer_queryset = refer_queryset.order_by('-created')

        # Handle type filtering and pagination efficiently
        include_imaging = order_types is None or "imaging" in order_types
        include_lab = order_types is None or "lab" in order_types
        include_referrals = order_types is None or "referral" in order_types

        # Calculate total counts using database COUNT queries
        imaging_count = imaging_orders_queryset.count() if include_imaging else 0
        lab_count = lab_orders_queryset.count() if include_lab else 0
        referral_count = refer_queryset.count() if include_referrals else 0
        total_count = imaging_count + lab_count + referral_count

        if priority == 'urgent':
            urgent_order_count = total_count
            routine_order_count = 0
        elif priority == 'routine':
            urgent_order_count = 0
            routine_order_count = total_count
        else:
            imaging_urgent_count = imaging_orders_queryset.filter(priority="Urgent").count() if include_imaging else 0
            referral_urgent_count = refer_queryset.filter(priority="Urgent").count() if include_referrals else 0
            urgent_order_count = imaging_urgent_count + referral_urgent_count
            routine_order_count = total_count - urgent_order_count

        if total_count == 0:
            return [JSONResponse({
                "logged_in_staff_id": logged_in_staff,
                "imaging_orders": [],
                "lab_orders": [],
                "referrals": [],
                "pagination": {
                    "current_page": 1,
                    "page_size": page_size,
                    "total_count": 0,
                    "total_pages": 0,
                    "has_next": False,
                    "has_previous": False,
                }
            }, status_code=HTTPStatus.OK)]

        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # Handle different scenarios for efficient pagination
        imaging_orders_data = []
        lab_orders_data = []
        referral_orders_data = []

        if priority in ['urgent', 'routine']:
            if include_imaging:
                imaging_slice = imaging_orders_queryset[start_index:min(end_index, start_index + page_size)]
                imaging_orders_data = [self._create_imaging_order_payload(io) for io in imaging_slice]
                page_size -= len(imaging_orders_data)
                start_index = max(0, start_index - imaging_count)
                end_index = start_index + page_size

            if include_lab and page_size > 0:
                lab_slice = lab_orders_queryset[start_index:min(end_index, start_index + page_size)]
                lab_orders_data = [self._create_lab_order_payload(lo) for lo in lab_slice]
                page_size -= len(lab_orders_data)
                start_index = max(0, start_index - lab_count)
                end_index = start_index + page_size

            if include_referrals and page_size > 0:
                referral_slice = refer_queryset[start_index:min(end_index, start_index + page_size)]
                referral_orders_data = [self._create_referral_order_payload(ro) for ro in referral_slice]
        else:
            if order_types and "imaging" in order_types:
                # Only imaging orders - use database slicing
                imaging_slice = imaging_orders_queryset[start_index:end_index]
                imaging_orders_data = [self._create_imaging_order_payload(io) for io in imaging_slice]

            if order_types and "lab" in order_types:
                # Only lab orders - use database slicing
                lab_slice = lab_orders_queryset[start_index:end_index]
                lab_orders_data = [self._create_lab_order_payload(lo) for lo in lab_slice]

            if order_types and "referral" in order_types:
                # Only referral orders - use database slicing
                referral_slice = refer_queryset[start_index:end_index]
                referral_orders_data = [self._create_referral_order_payload(ro) for ro in referral_slice]

            if not order_types:
                # Mixed orders - need to interleave results efficiently
                # Fetch enough records from each to ensure we can fill the page
                # This is a compromise for mixed sorting while avoiding loading all records
                fetch_size = min(page_size * page, 100)  # Cap at 100 to avoid excessive queries

                imaging_slice = list(imaging_orders_queryset[:fetch_size])
                lab_slice = list(lab_orders_queryset[:fetch_size])
                referral_slice = list(refer_queryset[:fetch_size])

                # Create combined list with sort keys
                combined_orders = []

                for io in imaging_slice:
                    combined_orders.append(self._create_imaging_order_payload(io, include_type=True))

                for lo in lab_slice:
                    combined_orders.append(self._create_lab_order_payload(lo, include_type=True))

                for ro in referral_slice:
                    combined_orders.append(self._create_referral_order_payload(ro, include_type=True))

                # Sort and paginate the combined results
                combined_orders.sort(key=lambda x: x.get('sort_key') or '', reverse=True)
                paginated_orders = combined_orders[start_index:end_index]

                # Separate back into imaging, lab, and referral orders
                for order in paginated_orders:
                    order.pop('sort_key', None)  # Remove sort key
                    order_type = order.pop('type', None)
                    if order_type == 'imaging':
                        imaging_orders_data.append(order)
                    elif order_type == 'lab':
                        lab_orders_data.append(order)
                    elif order_type == 'referral':
                        referral_orders_data.append(order)

        return [JSONResponse({
            "logged_in_staff_id": logged_in_staff,
            "imaging_orders": imaging_orders_data,
            "lab_orders": lab_orders_data,
            "referrals": referral_orders_data,
            "count": {
                "urgent": urgent_order_count,
                "routine": routine_order_count
            },
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            }
        }, status_code=HTTPStatus.OK)]

    @api.get("/task-comments")
    def get_task_comments(self) -> list[Response | Effect]:
        order_type = self.request.query_params.get("order_type")

        if not order_type:
            return [JSONResponse({"error": "order_type is required"}, status_code=HTTPStatus.BAD_REQUEST)]

        try:
            comments_data = []
            task_list = []

            # Handle referral orders using the task_list property
            if order_type.lower() == "referral":
                referral_id = self.request.query_params.get("referral_id")

                if not referral_id:
                    return [JSONResponse({"error": "referral_id is required for referral orders"}, status_code=HTTPStatus.BAD_REQUEST)]

                try:
                    referral = Referral.objects.get(id=referral_id, deleted=False)
                    task_list = list(referral.get_task_objects().filter(status=TaskStatus.OPEN))

                except Referral.DoesNotExist:
                    return [JSONResponse({"error": "Referral not found"}, status_code=HTTPStatus.NOT_FOUND)]

            # Handle imaging orders using the task_list property
            elif order_type.lower() == "imaging":
                imaging_id = self.request.query_params.get("imaging_id")

                if not imaging_id:
                    return [JSONResponse({"error": "imaging_id is required for imaging orders"}, status_code=HTTPStatus.BAD_REQUEST)]

                try:
                    imaging_order = ImagingOrder.objects.get(id=imaging_id, deleted=False)
                    task_list = list(imaging_order.get_task_objects().filter(status=TaskStatus.OPEN))

                except ImagingOrder.DoesNotExist:
                    return [JSONResponse({"error": "Imaging order not found"}, status_code=HTTPStatus.NOT_FOUND)]

            # For lab orders, we could implement similar logic if they get the task_list property
            elif order_type.lower() == "lab":
                # For now, return empty comments for lab orders
                # This could be extended when lab orders get the task_list property
                pass

            if task_list:
                # Get the last (most recent) task
                last_task = task_list[-1] if task_list else None

                if last_task:
                    # Get comments for this task
                    task_comments = last_task.comments.all().order_by('created').select_related('creator')

                    for comment in task_comments:
                        comments_data.append({
                            "id": str(comment.id),
                            "text": comment.body,
                            "author": comment.creator.credentialed_name if comment.creator else "Unknown",
                            "date": comment.created.strftime("%Y-%m-%d %H:%M"),
                            "task_id": str(last_task.id)
                        })

            return [JSONResponse({"comments": comments_data}, status_code=HTTPStatus.OK)]

        except Exception as e:
            return [JSONResponse({"error": f"Failed to load comments: {str(e)}"},
                                 status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

    @api.post("/task-comments")
    def add_task_comment(self) -> list[Response | Effect]:
        json_body = json.loads(self.request.body)
        patient_id = json_body.get("patient_id")
        comment = json_body.get("comment")
        task_id = json_body.get("task_id")
        order_type = json_body.get("order_type")
        order_id = json_body.get("order_id")
        log.info(f"Received task comment data: {json_body}")

        effects: list[Effect] = []
        if not task_id:
            task_id = uuid.uuid4()
            linked_task_type = None
            title = ""
            if order_type.lower() == "imaging":
                linked_task_type = AddTask.LinkableObjectType.IMAGING
                order = ImagingOrder.objects.get(id=order_id)
                title = f"Complete patient's imaging order to {order.imaging}" if order.imaging else "Complete patient's imaging order"
            elif order_type.lower() == "referral":
                linked_task_type = AddTask.LinkableObjectType.REFERRAL
                order = Referral.objects.get(id=order_id)
                title = f"Refer patient to {order.service_provider.full_name_and_specialty}" if order.service_provider else "Complete patient referral"

            if not linked_task_type:
                return [JSONResponse({"error": f"Invalid order type {order_type}"}, status_code=HTTPStatus.BAD_REQUEST)]

            effects.append(
                AddTask(
                    id=task_id,
                    author_id=self.request.headers["canvas-logged-in-user-id"],
                    title=title,
                    patient_id=patient_id,
                    linked_object_id=order_id,
                    linked_object_type=linked_task_type,
                ).apply()
            )

        effects.extend([
            AddTaskComment(task_id=task_id, body=comment, author_id=self.request.headers["canvas-logged-in-user-id"]).apply(),
            JSONResponse({}, status_code=HTTPStatus.OK)])

        return effects


class StaffFilterAPI(StaffSessionAuthMixin, SimpleAPI):

    cache_key = "FILTERS-"

    @api.post("/filter")
    def create_filters(self) -> list[Response | Effect]:
        logged_in_staff = self.request.headers["canvas-logged-in-user-id"]

        cache = get_cache()
        user_cache_key = f"{self.cache_key}-{logged_in_staff}"

        # get current filters
        user_filters = cache.get_or_set(user_cache_key, default=[])

        # get filters passed by in the URL
        new_filters = self.request.json()
        user_filters.append(new_filters)

        cache.set(user_cache_key, user_filters)

        return [JSONResponse({"filter": new_filters}, status_code=HTTPStatus.OK)]


    @api.get("/filters")
    def get_filters(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"])

        cache = get_cache()
        user_cache_key = f"{self.cache_key}-{logged_in_staff}"
        # get current filters
        user_filters = cache.get(user_cache_key)

        return [JSONResponse({"filters": user_filters}, status_code=HTTPStatus.OK)]


    @api.delete("/filter/<id>")
    def delete_filters(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"])

        filter_id = self.request.path_params["id"]

        cache = get_cache()
        user_cache_key = f"{self.cache_key}-{logged_in_staff}"
        # get current filters
        user_filters = cache.get(user_cache_key)
        user_filters = [ _filter for _filter in user_filters if _filter["id"] != filter_id ]
        cache.set(user_cache_key, user_filters)

        return [JSONResponse({"filters": user_filters}, status_code=HTTPStatus.OK)]