#!/bin/bash
cd website
ng build
cd ../
cdk deploy --all --require-approval never