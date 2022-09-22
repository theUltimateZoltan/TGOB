#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cards_dev.infrastructure import CardsInfra
from cards_dev.backend import CardsBackend
from cards_dev.s3_angular_website import CardsFrontEnd

app = cdk.App()
aws_environment = cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

infra_stack=CardsInfra(app, "CardsInfra", env=aws_environment)
CardsBackend(app, "CardsBackEnd", infrastructure=infra_stack, env=aws_environment)
CardsFrontEnd(app, "CardsFrontEnd", infrastructure=infra_stack, env=aws_environment)

app.synth()
