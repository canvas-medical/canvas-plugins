import arrow
from http import HTTPStatus

from django.db.models import Case, When, Value, Q, CharField

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import Response, JSONResponse
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import StaffSessionAuthMixin, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import ImagingOrder, LabOrder, Referral
from canvas_sdk.v1.data.staff import Staff
from logger import log


class OrderTrackingApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        return LaunchModalEffect(
            content=render_to_string("templates/worklist_orders.html", context={"patientChartApplication": "order_tracking.applications.patient_order_tracking_app:PatientOrderTrackingApplication"}),
            target=LaunchModalEffect.TargetType.PAGE,
        ).apply()


class OrderTrackingApi(StaffSessionAuthMixin, SimpleAPI):

    def _get_permalink_for_command(self, order: LabOrder | ImagingOrder | Referral, commandType: str) -> str:
        return f"noteId={order.note.dbid}&commandId={order.dbid}&commandType={commandType}"

    def _create_imaging_order_payload(self, imaging_order: ImagingOrder, include_type: bool = False) -> dict:
        """Create standardized payload for imaging order."""
        payload = {
            "patient_name": imaging_order.patient.preferred_full_name,
            "patient_id": str(imaging_order.patient.id),
            "dob": arrow.get(imaging_order.patient.birth_date).format("YYYY-MM-DD"),
            "status": imaging_order.order_status,
            "order": imaging_order.imaging,
            "created_date": imaging_order.created.isoformat() if imaging_order.created else None,
            "priority": imaging_order.priority,
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
        payload = {
            "patient_name": lab_order.patient.preferred_full_name,
            "patient_id": str(lab_order.patient.id),
            "dob": arrow.get(lab_order.patient.birth_date).format("YYYY-MM-DD"),
            "status": lab_order.order_status,
            "order": lab_order.ontology_lab_partner,
            "created_date": lab_order.created.isoformat() if lab_order.created else None,
            "sent_to": lab_order.ontology_lab_partner,
            "permalink": self._get_permalink_for_command(lab_order, "labOrder"),
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
        payload = {
            "patient_name": referral_order.patient.preferred_full_name,
            "patient_id": str(referral_order.patient.id),
            "dob": arrow.get(referral_order.patient.birth_date).format("YYYY-MM-DD"),
            "order": referral_order.internal_comment,
            "status": referral_order.order_status,
            "created_date": referral_order.created.isoformat() if referral_order.created else None,
            "priority": referral_order.priority,
            "sent_to": referral_order.service_provider.full_name_and_specialty if referral_order.service_provider else None,
            "permalink": self._get_permalink_for_command(referral_order, "referral"),
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

    @api.get("/orders")
    def orders(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"])

        # Get query parameters for filtering and pagination
        provider_id = self.request.query_params.get("provider_id")
        patient_id = self.request.query_params.get("patient_id")
        status = self.request.query_params.get("status")
        order_type = self.request.query_params.get("type")
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
        if provider_id:
            imaging_orders_queryset = imaging_orders_queryset.filter(ordering_provider__id=provider_id)
            lab_orders_queryset = lab_orders_queryset.filter(ordering_provider__id=provider_id)
            refer_queryset = refer_queryset.filter(note__provider__id=provider_id)

        if patient_id:
            imaging_orders_queryset = imaging_orders_queryset.filter(patient__id=patient_id)
            lab_orders_queryset = lab_orders_queryset.filter(patient__id=patient_id)
            refer_queryset = refer_queryset.filter(patient__id=patient_id)

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

        # Apply ordering for consistent results
        imaging_orders_queryset = imaging_orders_queryset.order_by('-created')
        lab_orders_queryset = lab_orders_queryset.order_by('-created')
        refer_queryset = refer_queryset.order_by('-created')

        # Handle type filtering and pagination efficiently
        include_imaging = order_type is None or order_type.lower() == "imaging"
        include_lab = order_type is None or order_type.lower() == "lab"
        include_referrals = order_type is None or order_type.lower() == "referral"

        # Calculate total counts using database COUNT queries
        imaging_count = imaging_orders_queryset.count() if include_imaging else 0
        lab_count = lab_orders_queryset.count() if include_lab else 0
        referral_count = refer_queryset.count() if include_referrals else 0
        total_count = imaging_count + lab_count + referral_count

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

        if order_type and order_type.lower() == "imaging":
            # Only imaging orders - use database slicing
            imaging_slice = imaging_orders_queryset[start_index:end_index]
            imaging_orders_data = [self._create_imaging_order_payload(io) for io in imaging_slice]

        elif order_type and order_type.lower() == "lab":
            # Only lab orders - use database slicing
            lab_slice = lab_orders_queryset[start_index:end_index]
            lab_orders_data = [self._create_lab_order_payload(lo) for lo in lab_slice]
        elif order_type and order_type.lower() == "referral":
            # Only referral orders - use database slicing
            referral_slice = refer_queryset[start_index:end_index]
            referral_orders_data = [self._create_referral_order_payload(ro) for ro in referral_slice]

        else:
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
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            }
        }, status_code=HTTPStatus.OK)]
