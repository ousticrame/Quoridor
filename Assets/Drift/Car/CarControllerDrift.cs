using System;
using System.Collections.Generic;
using System.Linq;
using Unity.Collections;
using Unity.VisualScripting;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public class CarControllerDrift : MonoBehaviour
{
    private RayCastSystem rcs;
    public NN network;
    public int ticksTaken = 0;
    public bool canMove;
    private Rigidbody _rigidbody;
    private GA_ManagerDrift _gaManager;
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
        this._gaManager = GameObject.Find("GA_Manager").GetComponent<GA_ManagerDrift>();
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
        Vector3 localVelocity = transform.InverseTransformDirection(this._rigidbody.linearVelocity);
        float normalized_speed_x = localVelocity.x / this.max_speed;
        float normalized_speed_z = localVelocity.z / this.max_speed;
        float[] metadata = {
            normalized_speed_x,
            normalized_speed_z,
            this._rigidbody.rotation.y,
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
        if (this._rigidbody.linearVelocity.magnitude > 0)
        {
            this.transform.rotation = Quaternion.Euler(new Vector3(0, steering * Time.fixedDeltaTime * 300f, 0) + this.transform.rotation.eulerAngles);
        }
        if (acceleration < -0.2f || acceleration > 0.2f)
        {
            this._rigidbody.linearVelocity += this.transform.forward * acceleration * this.acceleration_rate * Time.fixedDeltaTime;
        }
        this._rigidbody.linearVelocity = Vector3.ClampMagnitude(this._rigidbody.linearVelocity, this.max_speed);
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
