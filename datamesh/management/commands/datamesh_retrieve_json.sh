#!/usr/bin/env bash
PRODUCT=$(kubectl get pod -l app=projecttool-service -o jsonpath="{.items[0].metadata.name}" -n buildly)
DEV_PARTNER=$(kubectl get pod -l app=devpartner-service -o jsonpath="{.items[0].metadata.name}" -n buildly)
DECISION=$(kubectl get pod -l app=release-service -o jsonpath="{.items[0].metadata.name}" -n buildly)

cd ../../../
pwd

kubectl exec -it $PRODUCT -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 project_tool.product" > product.json
kubectl exec -it $PRODUCT -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 project_tool.credential" > credential.json
kubectl exec -it $PRODUCT -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 project_tool.release" > release.json
kubectl exec -it $DEV_PARTNER -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 dev_partner.timesheethour" > timesheethour.json
kubectl exec -it $DECISION -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 release.decision" > decision.json
kubectl exec -it $DECISION -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 release.feature" > feature.json
kubectl exec -it $DECISION -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 release.issue" > issue.json
kubectl exec -it $DECISION -n buildly -- bash -c "python manage.py dumpdata --format=json --indent=4 release.feedback" > feedback.json