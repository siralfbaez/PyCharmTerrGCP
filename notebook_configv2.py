COMPUTE_DEFAULT_SERVICE_ACCOUNT_BY_PROJECT = {
    'sab-dev-labs-research-9898': '1070023298433-compute@developer.gserviceaccount.com',
    'sab-dev-slps-gdd-9077': '138806986858-compute@developer.gserviceaccount.com'
}

def config(project_id, image_family, machine_type, requestor, expiration_hours):
    return {
        # 'serviceAccount': COMPUTE_DEFAULT_SERVICE_ACCOUNT_BY_PROJECT[project_id],
        "machineType": machine_type,
        "installGpuDriver": False,
        "bootDiskType": "PD_STANDARD",
        "dataDiskType": "PD_BALANCED",
        "dataDiskSizeGb": "100",
        "noRemoveDataDisk": False,
        "shieldedInstanceConfig": {
            "enableVtpm": True,
            "enableIntegrityMonitoring": True
        },
        # "noPublicIp": True,
        # "noProxyAccess": False,
       # ....
        "labels": {
            "createdby": requestor
        },
        "metadata": {
            "expiration_hours": expiration_hours
        },
        "vmImage": {
            "project": "deeplearning-platform-release",
            "imageFamily": image_family
        }
    }
