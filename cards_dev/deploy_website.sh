#!/bin/bash
cd website
ng build
cd ../
cdk deploy CardsFrontEnd