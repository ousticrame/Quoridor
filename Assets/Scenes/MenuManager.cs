using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Splines;
using UnityEngine.UI;

public static class MenuData {
    public static String fileName;
    public static bool training;
}

public class MenuManager : MonoBehaviour
{
    [SerializeField] Dropdown mapSelection;
    [SerializeField] Toggle trainingToggle;
    [SerializeField] InputField fileNameInput;
    [SerializeField] List<SplineContainer> maps;
    private SplineRoadCreator roadCreator;

    void Awake()
    {
        this.roadCreator = GameObject.Find("RoadManager").GetComponent<SplineRoadCreator>();
    }

    public void onMapSelectionChange()
    {
        this.roadCreator.DestroyMenuSpline();
        int index = this.mapSelection.value;
        Spline selectedMap = this.maps[index].Spline;
        this.roadCreator.CreateMenuSpline(selectedMap);
    }

    public void onStart()
    {
        MenuData.fileName = this.fileNameInput.text;
        MenuData.training = this.trainingToggle.isOn;
        // TODO: change map names
        switch (this.mapSelection.value)
        {
            case 0:
                SceneManager.LoadScene("Splines");
                break;
            case 1:
                SceneManager.LoadScene("Splines");
                break;
            case 2:
                SceneManager.LoadScene("Splines");
                break;
            case 3:
                SceneManager.LoadScene("Splines");
                break;
            case 4:
                SceneManager.LoadScene("Splines");
                break;
            default:
                break;
        }
    }
}
