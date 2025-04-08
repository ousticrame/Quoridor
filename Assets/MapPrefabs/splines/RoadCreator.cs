using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Splines;

public class SplineRoadCreator : MonoBehaviour
{
    public Spline spline;         // Reference to your spline object
    public GameObject roadPrefab; // Your road prefab
    public List<Vector3> checkpoints = new List<Vector3>(); // Store instantiated roads
    private List<GameObject> menuSpawnedGO;

    void Awake()
    {
        this.menuSpawnedGO = new List<GameObject>();
        GameObject spline_go = GameObject.FindGameObjectWithTag("Spline");
        if (spline_go != null) {
            this.spline = spline_go.GetComponent<SplineContainer>().Spline;
            CreateRoadAlongSpline();
        }
    }

    public void CreateMenuSpline(Spline spline)
    {
        float length = SplineUtility.CalculateLength(spline, transform.localToWorldMatrix);
        float spacing = 0.1f;
        int numSegments = Mathf.CeilToInt(length / spacing);
        for (int i = 0; i < numSegments; i++)
        {
            float t = i / (float)(numSegments - 1);
            Vector3 position = spline.EvaluatePosition(t);
            Vector3 tangent = spline.EvaluateTangent(t);
            Quaternion rotation = Quaternion.LookRotation(tangent);
            GameObject roadSegment = Instantiate(roadPrefab, position, rotation);
            this.menuSpawnedGO.Add(roadSegment);
        }
    }
    public void DestroyMenuSpline()
    {
        foreach (GameObject go in this.menuSpawnedGO)
        {
            Destroy(go);
        }
        this.menuSpawnedGO.Clear();
    }

    void CreateRoadAlongSpline()
    {
        // Get the length of the spline in world space
        float length = SplineUtility.CalculateLength(spline, transform.localToWorldMatrix);
        float spacing = 0.1f;  // Adjust this value based on your prefab size
        int numSegments = Mathf.CeilToInt(length / spacing);

        // Instantiate road segments along the spline
        for (int i = 0; i < numSegments; i++)
        {
            // Calculate the normalized value t (between 0 and 1)
            float t = i / (float)(numSegments - 1);

            // Get the position along the spline for the given normalized t
            Vector3 position = spline.EvaluatePosition(t);

            // Get the tangent (direction) at that position for rotation
            Vector3 tangent = spline.EvaluateTangent(t);
            Quaternion rotation = Quaternion.LookRotation(tangent);

            // Instantiate the prefab at that position with the correct rotation
            GameObject roadSegment = Instantiate(roadPrefab, position, rotation);

            // Store the instantiated object
            if (i % 25 != 24 || i >= numSegments - 100) {
                DestroyImmediate(roadSegment.transform.Find("Checkpoint").gameObject);
                continue;
            }
            this.checkpoints.Add(roadSegment.transform.Find("Checkpoint").transform.position);
        }
    }
}
