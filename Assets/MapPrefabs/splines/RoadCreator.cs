using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Splines;

public class SplineRoadCreator : MonoBehaviour
{
    public SplineContainer splineContainer;         // Reference to your spline object
    public Spline spline;         // Reference to your spline object
    public GameObject roadPrefab; // Your road prefab
    public List<Vector3> checkpoints = new List<Vector3>(); // Store instantiated roads

    void Awake()
    {
        this.spline = this.splineContainer.Spline;
        CreateRoadAlongSpline();
    }

    void CreateRoadAlongSpline()
    {
        // Get the length of the spline in world space
        float length = SplineUtility.CalculateLength(spline, transform.localToWorldMatrix);
        float spacing = 0.5f;  // Adjust this value based on your prefab size
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
            if (i % 10 != 9) {
                DestroyImmediate(roadSegment.transform.Find("Checkpoint").gameObject);
                continue;
            }
            this.checkpoints.Add(roadSegment.transform.Find("Checkpoint").transform.position);
        }
    }
}
