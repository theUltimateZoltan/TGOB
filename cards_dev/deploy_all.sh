#!/bin/bash
cd website
npm install
ng build
cd ../
cdk deploy --all --require-approval never