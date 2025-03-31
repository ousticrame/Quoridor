using System;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Rendering;

public class DroneController : MonoBehaviour
{
    private RayCastSystem rcs;
    public NN network;
    public int ticksTaken = 0;
    public bool canMove;
    private Rigidbody _rigidbody;
    private GA_Manager _gaManager;
    public int score;
    public List<Vector3> checkpoints;
    private List<GameObject> alreadyHitCheckpoints;

    void Awake()
    {
        this.alreadyHitCheckpoints = new List<GameObject>();
        this.score = 0;
        this.canMove = true;
        this.ticksTaken = 0;
        this.rcs = this.GetComponent<RayCastSystem>();
        this._rigidbody = this.GetComponent<Rigidbody>();
        this._gaManager = GameObject.Find("GA_Manager").GetComponent<GA_Manager>();
    }

    /*void FixedUpdate()
    {
        this.Move();
    }*/
    public void Move()
    {
        if (!this.canMove)
        {
            return;
        }
        this.ticksTaken++;
        float[] inputs = this.BuildInputs();
        float[] outputs = this.network.Forward(inputs);
        this.ProcessOutputs(outputs);
    }

    public float[] BuildInputs()
    {
        float[] raycasts = this.rcs.getDistances();
        /*float[] distances = {
            Math.Abs(this.transform.position.x - this.checkpoints[0].x),
            Math.Abs(this.transform.position.y - this.checkpoints[0].y),
            Math.Abs(this.transform.position.z - this.checkpoints[0].z),
            this.transform.rotation.eulerAngles.y
        };*/

        List<float> inputs = new List<float>();
        inputs.AddRange(raycasts);
        //inputs.AddRange(distances);

        return inputs.ToArray();
    }

    public void ProcessOutputs(float[] outputs)
    {
        float y_up = outputs[0];
        float y_rotation = outputs[1];
        float z_forward = outputs[2];
        this.transform.rotation = Quaternion.Euler(new Vector3(0, y_rotation, 0) * 2f + this.transform.rotation.eulerAngles);
        this._rigidbody.linearVelocity = this.transform.forward * z_forward * 5f + this.transform.up * y_up;
    }


    void OnTriggerEnter(Collider other)
    {
        if (other.tag.Equals("Wall"))
        {
            this.StopMoving();
        }
        else if (other.tag.Equals("Checkpoint") && !this.alreadyHitCheckpoints.Contains(other.gameObject))
        {
            this.alreadyHitCheckpoints.Add(other.gameObject);
            this.score += 1;
            this.checkpoints.RemoveAt(0);
            if (this.checkpoints.Count == 0)
            {
                this.StopMoving();
            }
        }
    }

    public void StopMoving()
    {
        this.canMove = false;
        this._rigidbody.linearVelocity = Vector3.zero;
        this._gaManager.nb_drones_alives -= 1;
    }
}
