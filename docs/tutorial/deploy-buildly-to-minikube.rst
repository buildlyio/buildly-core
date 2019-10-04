Deploy Buildly to Minikube
==========================

Overview
--------

This tutorial explains how to deploy `Buildly <https://buildly.io/buildly-core/>`_ to an existing Minikube cluster. 

Once you deploy Buildly to your cluster, it will be able to start receiving requests, and connecting with all of your other services.

Deploy Buildly with Helm
------------------------

Requirements
^^^^^^^^^^^^

The only requirements for this tutorial are:

1.  A `Minikube <https://minikube.sigs.k8s.io/>`_ instance up and running in your local machine.
2.  `kubectl <https://kubernetes.io/docs/reference/kubectl/overview/>`_ installed and configured to access your `Minikube <https://minikube.sigs.k8s.io/>`_ instance.
3.  `Helm <https://helm.sh/>`_ also installed and configured.
4.  Have a `PostgreSQL <https://www.postgresql.org/>`_ database instance up and running.

Ensure minikube and kubectl are running by entering:

.. code-block:: bash

   minikube status
   kubectl cluster-info
   kubectl get nodes

Ensure helm is initalized by running:

.. code-block:: bash

   helm init


Deploy Buildly to Kubernetes clusters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first thing you need to do is clone Buildly Helm Charts repository, where you can find the right charts to deploy Buildly to any `Kubernetes <https://kubernetes.io/>`_ cluster including local Minikube instances. 

Run the following command to clone Buildly Helm Charts repository:

.. code-block:: bash

   git clone https://github.com/buildlyio/helm-charts.git


Now, you need to create a namespace to deploy Buildly and you do it running:

.. code-block:: bash

   kubectl create namespace buildly

The last but not least, you will execute the Helm charts but you need to pass the database connection information to Buildly when running the charts, otherwise, it won't work because it wasn't able to connect to the dabatase. You need to provide the database host, port(defaul=5432), username(base64 encrypted), and password(base64 encrypted). You run the following command replacing the fake data with your database connection info:

.. code-block:: bash

   helm install . --name buildly-core --namespace buildly \
   --set configmap.data.DATABASE_HOST="<db-host>" \
   --set configmap.data.DATABASE_PORT="<db-port>" \
   --set secret.data.DATABASE_USER="<db-user>" \
   --set secret.data.DATABASE_PASSWORD="<db-pass>"


After that you should see a Buildly Core instance running in your Minikube dashboard. It has also created a ClusterIP and Ingress, so if you have a certificate manager and everything setup it should also be exposed externally. If you prefer to create a LoadBalancer instead, you can just delete the Ingress instance that was created.

..  Deploy Buildly with Kompose
	---------------------------

	Requirements
	^^^^^^^^^^^^

	The requirements for this tutorial are:

	1.  A `Minikube <https://minikube.sigs.k8s.io/>`_ instance up and running in your local machine.
	2.  `kubectl <https://kubernetes.io/docs/reference/kubectl/overview/>`_ installed and configured to access your `Minikube <https://minikube.sigs.k8s.io/>`_ instance.
	3.  `Kompose <https://kompose.io/>`_ installed.
	4.  A local `Docker <https://www.docker.com/>`_ registry listening to the port 5000.

	Ensure minikube and kubectl are running by entering:

	.. code-block:: bash

	minikube status
	kubectl cluster-info
	kubectl get nodes

	Deploy Buildly to Kubernetes clusters
	^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	The first thing you need to do is clone `Buildly Core <https://buildly.io/buildly-core/>`_ source code. Also follow the instructions in :ref:`connect service to buildly` but also make sure it includes a `docker-compose` file for this tutorial.

	Run the following command to clone Buildly Core repository:

	.. code-block:: bash

	git clone https://github.com/buildlyio/buildly-core.git


	Now, you need to navigate to the Buildly Core folder and change the image of `Buildly <https://buildly.io/buildly-core/>`_ in the `docker-compose.yml` file, with your prefered text editor, to `Image: localhost:5000/buildly`.

	Run the following command to deploy it to your `Minikube <https://minikube.sigs.k8s.io/>`_ cluster:

	.. code-block:: bash

	kompose up