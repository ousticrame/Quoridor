using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class MenuManager : MonoBehaviour
{
    [SerializeField] Dropdown mapSelection;
    [SerializeField] List<GameObject> maps;
    private GameObject spawnedMapPreview;
    private Vector3 cameraPos = new Vector3(625.802f, 408.8869f, -525.3568f);
    public void onMapSelectionChange()
    {
        if (this.spawnedMapPreview != null)
        {
            Destroy(this.spawnedMapPreview);
        }
        int index = this.mapSelection.value;
        GameObject selectedMap = maps[index];
        this.spawnedMapPreview = Instantiate(selectedMap, cameraPos + new Vector3(0, 0, 100), Quaternion.identity);
    }
}
