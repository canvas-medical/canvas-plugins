import arrow
from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import Response, JSONResponse
from canvas_sdk.handlers.application import Application
from canvas_sdk.handlers.simple_api import StaffSessionAuthMixin, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import ImagingOrder, LabOrder
from canvas_sdk.v1.data.staff import Staff


class OrderTrackingApplication(Application):
    """An embeddable application that can be registered to Canvas."""

    def on_open(self) -> Effect:
        return LaunchModalEffect(
            content=render_to_string("templates/worklist_orders.html"),
        ).apply()


class OrderTrackingApi(StaffSessionAuthMixin, SimpleAPI):
    @api.get("/providers")
    def providers(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"])

        imaging_ordering_providers = [
            {
                "preferred_name": f"{io.ordering_provider.first_name} {io.ordering_provider.last_name}",
                "id": str(io.ordering_provider.id),
            } for io in ImagingOrder.objects.all()]

        lab_ordering_providers = [
            {
                "preferred_name": f"{lo.ordering_provider.first_name} {lo.ordering_provider.last_name}",
                "id": str(lo.ordering_provider.id),
            } for lo in LabOrder.objects.all()
        ]

        return [JSONResponse({
            "logged_in_staff_id": logged_in_staff,
            "imaging_ordering_providers": imaging_ordering_providers,
            "lab_orders_providers": lab_ordering_providers,
        }, status_code=HTTPStatus.OK)]

    @api.get("/orders")
    def orders(self) -> list[Response | Effect]:
        logged_in_staff = Staff.objects.values_list("id", flat=True).get(
            id=self.request.headers["canvas-logged-in-user-id"])

        # Get query parameters for filtering and pagination
        provider_id = self.request.query_params.get("provider_id")
        order_type = self.request.query_params.get("type")
        page = int(self.request.query_params.get("page", 1))
        page_size = int(self.request.query_params.get("page_size", 20))

        # Build querysets with filters and select_related for efficiency
        imaging_orders_queryset = ImagingOrder.objects.select_related('patient', 'ordering_provider')
        lab_orders_queryset = LabOrder.objects.select_related('patient', 'ordering_provider')

        # Apply provider filter if specified
        if provider_id:
            imaging_orders_queryset = imaging_orders_queryset.filter(ordering_provider__id=provider_id)
            lab_orders_queryset = lab_orders_queryset.filter(ordering_provider__id=provider_id)

        # Apply ordering for consistent results
        imaging_orders_queryset = imaging_orders_queryset.order_by('-created')
        lab_orders_queryset = lab_orders_queryset.order_by('-created')

        # Handle type filtering and pagination efficiently
        include_imaging = order_type is None or order_type.lower() == "imaging"
        include_lab = order_type is None or order_type.lower() == "lab"

        # Calculate total counts using database COUNT queries
        imaging_count = imaging_orders_queryset.count() if include_imaging else 0
        lab_count = lab_orders_queryset.count() if include_lab else 0
        total_count = imaging_count + lab_count

        if total_count == 0:
            return [JSONResponse({
                "logged_in_staff_id": logged_in_staff,
                "imaging_orders": [],
                "lab_orders": [],
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

        if order_type and order_type.lower() == "imaging":
            # Only imaging orders - use database slicing
            imaging_slice = imaging_orders_queryset[start_index:end_index]
            imaging_orders_data = [
                {
                    "patient_name": io.patient.preferred_full_name,
                    "dob": arrow.get(io.patient.birth_date).format("YYYY-MM-DD"),
                    "status": io.patient.status,
                    "order": io.imaging,
                    "created_date": io.created.isoformat() if hasattr(io, 'created') else None,
                    "ordering_provider": {
                        "preferred_name": f"{io.ordering_provider.first_name} {io.ordering_provider.last_name}",
                        "id": str(io.ordering_provider.id),
                    }
                } for io in imaging_slice
            ]

        elif order_type and order_type.lower() == "lab":
            # Only lab orders - use database slicing
            lab_slice = lab_orders_queryset[start_index:end_index]
            lab_orders_data = [
                {
                    "patient_name": lo.patient.preferred_full_name,
                    "dob": arrow.get(lo.patient.birth_date).format("YYYY-MM-DD"),
                    "order": lo.ontology_lab_partner,
                    "created_date": lo.created.isoformat() if hasattr(lo, 'created') else None,
                    "ordering_provider": {
                        "preferred_name": f"{lo.ordering_provider.first_name} {lo.ordering_provider.last_name}",
                        "id": str(lo.ordering_provider.id),
                    }
                } for lo in lab_slice
            ]

        else:
            # Mixed orders - need to interleave results efficiently
            # Fetch enough records from each to ensure we can fill the page
            # This is a compromise for mixed sorting while avoiding loading all records
            fetch_size = min(page_size * page, 100)  # Cap at 100 to avoid excessive queries
            
            imaging_slice = list(imaging_orders_queryset[:fetch_size])
            lab_slice = list(lab_orders_queryset[:fetch_size])
            
            # Create combined list with sort keys
            combined_orders = []
            
            for io in imaging_slice:
                combined_orders.append({
                    "patient_name": io.patient.preferred_full_name,
                    "dob": arrow.get(io.patient.birth_date).format("YYYY-MM-DD"),
                    "status": io.patient.status,
                    "order": io.imaging,
                    "type": "imaging",
                    "created_date": io.created.isoformat() if hasattr(io, 'created') else None,
                    "ordering_provider": {
                        "preferred_name": f"{io.ordering_provider.first_name} {io.ordering_provider.last_name}",
                        "id": str(io.ordering_provider.id),
                    },
                    "sort_key": io.created if hasattr(io, 'created') else None
                })
            
            for lo in lab_slice:
                combined_orders.append({
                    "patient_name": lo.patient.preferred_full_name,
                    "dob": arrow.get(lo.patient.birth_date).format("YYYY-MM-DD"),
                    "order": lo.ontology_lab_partner,
                    "type": "lab",
                    "created_date": lo.created.isoformat() if hasattr(lo, 'created') else None,
                    "ordering_provider": {
                        "preferred_name": f"{lo.ordering_provider.first_name} {lo.ordering_provider.last_name}",
                        "id": str(lo.ordering_provider.id),
                    },
                    "sort_key": lo.created if hasattr(lo, 'created') else None
                })
            
            # Sort and paginate the combined results
            combined_orders.sort(key=lambda x: x.get('sort_key') or '', reverse=True)
            paginated_orders = combined_orders[start_index:end_index]
            
            # Separate back into imaging and lab orders
            for order in paginated_orders:
                order.pop('sort_key', None)  # Remove sort key
                if order.get('type') == 'imaging':
                    order.pop('type', None)
                    imaging_orders_data.append(order)
                else:
                    order.pop('type', None)
                    lab_orders_data.append(order)

        return [JSONResponse({
            "logged_in_staff_id": logged_in_staff,
            "imaging_orders": imaging_orders_data,
            "lab_orders": lab_orders_data,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
            }
        }, status_code=HTTPStatus.OK)]
