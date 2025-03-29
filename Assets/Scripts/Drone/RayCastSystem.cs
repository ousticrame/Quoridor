using System.Collections.Generic;
using UnityEngine;

public class RayCastSystem : MonoBehaviour
{
    [SerializeField] public int numRaycasts;
    [SerializeField] int angleBetweenRaycasts;
    [SerializeField] int raycastLength;
    [SerializeField] List<string> hittableTags;
    [SerializeField] float raycastsStartHeight;

    private float[] distances;

    private void Awake()
    {
        this.distances = new float[this.numRaycasts];
        for (int i = 0; i < this.numRaycasts; i++)
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
        RaycastHit hit;
        for (int i = 0; i < this.numRaycasts; i++)
        {
            float angle = ((2 * i + 1 - this.numRaycasts) * this.angleBetweenRaycasts / 2);

            Quaternion rotation = Quaternion.AngleAxis(angle, Vector3.up);
            Vector3 rayDirection = rotation * this.transform.forward;

            Vector3 rayStart = this.transform.position + Vector3.up * this.raycastsStartHeight;

            if (Physics.Raycast(rayStart, rayDirection, out hit, this.raycastLength))
            {
                
                if (this.hittableTags.Contains(hit.transform.gameObject.tag))
                {
                    
                    this.distances[i] = hit.distance;
                    Debug.DrawRay(rayStart, rayDirection * hit.distance, Color.red);
                }
                else
                {
                    this.distances[i] = this.raycastLength;
                    Debug.DrawRay(rayStart, rayDirection * hit.distance, Color.green);
                }
            }
            else
            {
                Debug.DrawRay(rayStart, rayDirection * this.raycastLength, Color.white);
                this.distances[i] = this.raycastLength;
            }
        }
    }
}
