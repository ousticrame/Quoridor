using UnityEngine;
using UnityEngine.Splines;
using Unity.Mathematics;

[RequireComponent(typeof(MeshFilter))]
public class MeshDeformer : MonoBehaviour
{
    [SerializeField] public SplineContainer splineContainer;
    public float splineLength = 10f; // Match this to mesh length in Z
    public bool updateInEditor = true;

    private Mesh originalMesh;
    private Mesh deformedMesh;

    void Awake()
    {
        MeshFilter mf = GetComponent<MeshFilter>();
        originalMesh = mf.sharedMesh;
        deformedMesh = Instantiate(originalMesh);
        mf.sharedMesh = deformedMesh;
        DeformMesh();
    }

    void Update()
    {
        if (updateInEditor)
        {
            DeformMesh();
        }
    }

    void DeformMesh()
    {
        if (splineContainer == null || originalMesh == null)
            return;

        Vector3[] verts = originalMesh.vertices;
        Vector3[] newVerts = new Vector3[verts.Length];

        for (int i = 0; i < verts.Length; i++)
        {
            Vector3 v = verts[i];
            float t = Mathf.Clamp01(v.z / splineLength);
            float3 fPos, fTangent;
            SplineUtility.Evaluate(splineContainer.Spline, t, out fPos, out fTangent, out _);

            Vector3 pos = (Vector3)fPos;
            Vector3 tangent = (Vector3)fTangent;

            // Construct a rotation from tangent
            Quaternion rot = Quaternion.LookRotation(tangent.normalized, Vector3.up);

            // Local offset
            Vector3 localOffset = new Vector3(v.x, v.y, 0);
            Vector3 worldPos = pos + rot * localOffset;

            newVerts[i] = transform.InverseTransformPoint(worldPos);
        }

        deformedMesh.vertices = newVerts;
        deformedMesh.RecalculateNormals();
        deformedMesh.RecalculateBounds();
    }
}
