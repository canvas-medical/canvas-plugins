import factory

from canvas_sdk.v1.data import Organization


class OrganizationFactory(factory.django.DjangoModelFactory[Organization]):
    """Factory for creating Organization."""

    class Meta:
        model = Organization

    short_name = "Canvas Medical"
    full_name = "Canvas Medical, Inc."
    logo_url = "https://s3-us-west-2.amazonaws.com/canvas-pcp-assets/canvas_logo_large.png"
    background_image_url = "https://s3-us-west-2.amazonaws.com/canvas-pcp-assets/santa-cruz-low.jpg"
    background_gradient = (
        "linear-gradient(to top, rgb(231, 201, 154) 0%, rgb(220, 210, 192) 29%, "
        "rgb(156, 175, 191) 90%, rgb(147, 166, 189) 100%)"
    )
    tax_id = "123456"
