# PDB Mirror

Online service for mirroring existing PDB archive. This app stores compressed `cif` files in `gz` format. App offers public API for checking latest updated PDB IDs and option to download compressed files.

## Running locally

**`Ubuntu` or similar Linux distribution is assumed.**

### Requirements:

- Docker installed (guide [here](https://docs.docker.com/engine/install/ubuntu/)).
- `docker compose` utility installed (guide [here](https://docs.docker.com/desktop/setup/install/linux/ubuntu/)).


Docker compose uses configurations in `backend/Dockerfile`.

App as a whole can be run using `docker-compose.yaml` file for development enviroment. 
Use following commands to build and run the app:

```
docker compose -f docker/docker-compose.yaml build --no-cache
docker compose -f docker/docker-compose.yaml up
```
Backend uses `--reload` option, meaning code changes in FastAPI's code are propagated to docker container.

### Accessing database via `psql`

#### Requirements:
- `psql` utility (install using `sudo apt install postgresql-client`)

Assuming `docker compose up` command running, use following command and when prompted for password use `admin` or the password you have set in `docker-compose` file:

```
psql -h 172.20.0.4 -U admin -d pdb_mirror 
```

## Deployment on Kubernetes

### Requirements:
- `kubectl` utility installed (guide [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)).
- Available Kubernetes enviroment.
- Secrets created in Kubernetes enviroment.
- Images available on image registry of your choice for backend image.

#### Optional
- `kompose` utility installed (guide [here](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)).

### Building production images

**Don't forget to update image urls in corresponding `kubernetes/*-deployment.yaml` files.**
Build images:

- Backend:
```
docker build -t REGISTRY_URL/USERNAME/IMAGE_NAME:TAG -f Dockerfile-prod . --no-cache
docker push REGISTRY_URL/USERNAME/IMAGE_NAME:TAG
```

### Secrets

For this project `Rancher` management platform was used to create secrets. 


#### Creating secrets
Step by step:

1. Login to Rancher.
2. Navigate to your cluster.
3. Navigate to `Storage` on left sidebar.
4. Navigate to `Secrets` option under `Storage` in left sidebar.
5. Click `Create` in the right top corner under your profile icon.
6. Choose `Opaque` secret type.
7. Fill in the `Name` with name you plan to use in configuration files (default: `pdb-mirrors-creds`).
8. Add necessary variables under `Data` (click on `Add` to add more):
    - db-host
    - db-name
    - db-user
    - db-pass
    - db-port
9. Click `Create` in the right bottom corner.


#### Editing secrets
1. Follow steps 1-4 from [Creating secrets](#creating-secrets).
2. Click on an existing name of a secret you want to edit.
3. Click on 3 dots icon in top right corner under your profile icon.
4. Click `Edit Config` in dropdown menu.
5. Add/Edit/Remove your secrets.
6. Click `Save` in bottom right corner.

### Creating/updating pods


```
kubectl apply -f kubernetes -n YOUR_NAMESPACE
```


### Interacting with pods remotely.

If your Kubernetes solution doesn't support web terminal or you simply want to use your terminal, you first need to get pod identifiers:

```
kubectl get pods -n YOUR_NAMESPACE
```

Then you can connect to your pods using:
- Backend (bash):

```
kubectl exec -it -n YOUR_NAMESPACE POD_ID -- bash
```

### (Optional) Generating new configuration files.
In `kubernetes` you can find configuration files for deployment on Kubernetes platform. These files were manually adjusted after using `Kompose` utility to generate initial version from existing `docker-compose-prod.yaml` files. 


### Caution
There are a few caveats to consider when generating your own configuration file. Firstly, keep in mind that produced configuration files are not complete and require adding additional files (ingress, service) and tweaking security options and secrets (use existing files in `kubernetes/` for reference). 

Step by step:

1. Update image paths in `docker-compose-prod.yaml` file to use repository URLs to your built images.

2. Create and move to folder where you want your configuration files to be stored:

```
mkdir FOLDER_NAME

cd FOLDER_NAME
```

3. Run `kompose`:

```kompose -f PATH_TO_DOCKER_COMPOSE_FILE convert ```

