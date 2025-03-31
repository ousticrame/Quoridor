using System;
using System.Collections.Generic;
using System.Linq;
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
        /*for (int i = 0; i < raycasts.Length; i++)
        {
            raycasts[i] = raycasts[i] / (float) this.rcs.raycastLength;
        }*/
        Vector2 drone_forward_vec = new Vector2(this.transform.forward.x, this.transform.forward.z);
        Vector2 checkpoint_pos_vec = new Vector2((this.checkpoints[0] - this.transform.position).x, (this.checkpoints[0] - this.transform.position).z);
        float angle = Vector2.SignedAngle(drone_forward_vec.normalized, checkpoint_pos_vec.normalized);
        //Debug.Log($"{angle} degres, {this.checkpoints[0]}");
        float y_dist = this.checkpoints[0].y - this.transform.position.y;
        y_dist = ((1f / (1f + Mathf.Exp(-y_dist))) - 0.5f) * 2f;
    
        float[] metadata = {
            angle,
            y_dist,
        };

        List<float> inputs = new List<float>();
        inputs.AddRange(raycasts);
        inputs.AddRange(metadata);

        return inputs.ToArray();
    }

    public void ProcessOutputs(float[] outputs)
    {
        float y_up = outputs[0];
        float y_rotation = outputs[1];
        float z_forward = Mathf.Max(outputs[2], 0);
        this.transform.rotation = Quaternion.Euler(new Vector3(0, y_rotation, 0) * 2f + this.transform.rotation.eulerAngles);
        this._rigidbody.linearVelocity = this.transform.forward * z_forward * 5f + this.transform.up * y_up * 3f;
    }


    void OnTriggerEnter(Collider other)
    {
        if (other.tag.Equals("Wall"))
        {
            this.StopMoving();
        }
        else if (other.tag.Equals("Checkpoint") && !this.alreadyHitCheckpoints.Contains(other.gameObject))
        {
            if (other.gameObject.transform.position != this.checkpoints[0]) // he cheated (skipped a checkpoint) (skibiddi)
            {
                this.StopMoving();
                return;
            }
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
