"""jjjquery infrastructure as code."""

import aws_cdk as cdk
import aws_cdk.aws_certificatemanager as acm
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_route53 as route53
import aws_cdk.aws_route53_targets as targets


class Jjjquery(cdk.App):
    """Deploys cloud-fronted Lambda jjjfunction."""

    def __init__(self) -> None:
        super().__init__()
        stack = JjjqueryStack(
            self,
            id="JjjqueryStack",
            # Join the global single point of failure. Custom CloudFront certificates
            # HAVE to reside in us-east-1 anyway...
            env=cdk.Environment(region="us-east-1"),
            # Show hosted zones with $ aws route53 list-hosted-zones --output yaml
            hosted_zone_id="Z0932427366G4DNP1CWB",
            zone_name="brodie.id.au.",
        )
        cdk.Tags.of(self).add("project", stack.domain_name)


class JjjqueryStack(cdk.Stack):
    """A cloud-fronted Lambda@Edge function running a Marimo app.

    Human -> CloudFront -> Lambda@Edge -> mangum -> marimo -> update slider value 😂

    Handles
    - Lambda function bundling
    - Certificate creation and renewal
    - DNS records
    - Bucket for logs
    """

    def __init__(
        self,
        scope,
        id: str,
        env: cdk.Environment,
        hosted_zone_id: str,
        zone_name: str,
    ):
        # Trim zone name's trailing dot to construct jjjomain name.
        self.domain_name = f"jjjquery.{zone_name[:-1]}"
        super().__init__(
            scope,
            id,
            description=f"{self.domain_name} stack",
            env=env,
        )

        # Reference an existing hosted zone...
        hosted_zone = route53.PublicHostedZone.from_public_hosted_zone_attributes(
            self,
            "HostedZone",
            hosted_zone_id=hosted_zone_id,
            zone_name=zone_name,
        )

        # ...to create a certificate.
        certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name=self.domain_name,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # A CloudFront distribution serves from Lambda@Edge origin.
        distribution = cloudfront.Distribution(
            scope=self,
            id="Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                # Lambda@Edge should return a response before requests are sent
                # to origin. I think this has to at least be a registered domain.
                # example.local and example.test didn't work. example.com works.
                # I'm not sure if a web server needs to be running.
                origin=origins.HttpOrigin(domain_name=self.domain_name),  # pyright: ignore
            ),
            certificate=certificate,
            domain_names=[self.domain_name],
            enable_logging=True,
            # Use cheapest class of edge locations.
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
        )

        # Create an alias record for the CloudFront distribution.
        route53.ARecord(
            scope=self,
            id="ARecord",
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
            zone=hosted_zone,
            record_name=self.domain_name,
        )


if __name__ == "__main__":
    Jjjquery().synth()
