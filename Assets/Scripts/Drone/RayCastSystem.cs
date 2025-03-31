using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class RayCastSystem : MonoBehaviour
{
    [SerializeField] int raycastLength;

    [SerializeField] List<string> hittableTags;

    [SerializeField] List<Transform> raycast_transforms;

    private float[] distances;

    private void Awake()
    {
        this.distances = new float[raycast_transforms.Count];
        for (int i = 0; i < raycast_transforms.Count; i++)
        {
            this.distances[i] = this.raycastLength;
        }
    }

    public float[] getDistances()
    {
        return this.distances;
    }

    private void FixedUpdate()
    {
        this.CreateRaycasts();
    }

    public void CreateRaycasts()
    {
        int i = 0;
        foreach (Transform t in this.raycast_transforms)
        {
            RaycastHit[] hits = Physics.RaycastAll(t.position, t.forward, this.raycastLength);
            int index = -1;
            if (hits.Length > 0)
            {
                index = hits.ToList().ConvertAll(x => x.transform.gameObject.tag).IndexOf(this.hittableTags[0]);
            }
            if (index > -1)
            {
                this.distances[i++] = hits[index].distance;
                Debug.DrawRay(t.position, t.forward * hits[index].distance, Color.red);
            }
            else
            {
                Debug.DrawRay(t.position, t.forward * this.raycastLength, Color.white);
                this.distances[i++] = this.raycastLength;
            }
        }
    }
}
