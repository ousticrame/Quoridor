using System;
using System.Collections.Generic;
using System.Linq;
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public class CarController : MonoBehaviour
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
    private bool grounded = false;

    // SPEED VARS
    public float current_speed;
    [SerializeField] private float max_speed;
    [SerializeField] private float acceleration_rate;

    void Awake()
    {
        this.alreadyHitCheckpoints = new List<GameObject>();
        this.score = 0;
        this.canMove = true;
        this.ticksTaken = 0;
        this.current_speed = 0f;
        this.rcs = this.GetComponent<RayCastSystem>();
        this._rigidbody = this.GetComponent<Rigidbody>();
        this._gaManager = GameObject.Find("GA_Manager").GetComponent<GA_Manager>();
    }

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
        for (int i = 0; i < raycasts.Length; i++)
        {
            raycasts[i] = raycasts[i] / (float) this.rcs.raycastLength;
        }
        Vector2 my_forward_vec = new Vector2(this.transform.forward.x, this.transform.forward.z);
        Vector2 checkpoint_pos_vec = new Vector2((this.checkpoints[0] - this.transform.position).x, (this.checkpoints[0] - this.transform.position).z);
        float angle = Vector2.SignedAngle(my_forward_vec.normalized, checkpoint_pos_vec.normalized) / 180f;
        float normalized_speed = this.current_speed / this.max_speed;
    
        float[] metadata = {
            angle,
            normalized_speed,
        };

        List<float> inputs = new List<float>();
        inputs.AddRange(raycasts);
        inputs.AddRange(metadata);
        return inputs.ToArray();
    }

    public void ProcessOutputs(float[] outputs)
    {
        float steering = outputs[0];
        float acceleration = outputs[1];
        this.grounded = this.grounded || Physics.Raycast(this.transform.position, -Vector3.up, 2.2f);
        if (!this.grounded)
        {
            //this._rigidbody.linearVelocity = this.transform.up * -0.5f;
            this.transform.position -= this.transform.up * 0.5f;
            return;
        }
        if (this.current_speed > 0)
        {
            this.transform.rotation = Quaternion.Euler(new Vector3(0, steering * Time.fixedDeltaTime * 100f, 0) + this.transform.rotation.eulerAngles);
        }
        if (acceleration < -0.2f)
        {
            this.current_speed += acceleration * this.acceleration_rate * Time.fixedDeltaTime;
            this.current_speed = Mathf.Max(this.current_speed, 0);
        }
        else if (acceleration > 0.2f)
        {
            this.current_speed += acceleration * this.acceleration_rate * Time.fixedDeltaTime;
            this.current_speed = Mathf.Min(this.current_speed, this.max_speed);
        }
        this._rigidbody.linearVelocity = this.transform.forward * this.current_speed;
        //this.transform.position += this.transform.forward * this.current_speed / this.max_speed;
        //Debug.Log(this.current_speed);
    }


    void OnTriggerEnter(Collider other)
    {
        if (!this.canMove)
        {
            return;
        }
        if (other.tag.Equals("Wall"))
        {
            this.StopMoving();
        }
        if (other.tag.Equals("Checkpoint"))
        {
            if (other.gameObject.transform.position != this.checkpoints[0]) // he cheated (skipped a checkpoint or went back) (skibiddi)
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
        this._gaManager.nb_cars_alives -= 1;
    }
}
