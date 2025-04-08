using System.Collections.Generic;
using UnityEngine;

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
    public Vector3 MoveForce;
    [SerializeField] private float max_speed;
    [SerializeField] private float acceleration_rate;
    private Vector3 windForce;

    void Awake()
    {
        this.alreadyHitCheckpoints = new List<GameObject>();
        this.score = 0;
        this.canMove = true;
        this.ticksTaken = 0;
        this.rcs = this.GetComponent<RayCastSystem>();
        this._rigidbody = this.GetComponent<Rigidbody>();
        this._gaManager = GameObject.Find("GA_Manager").GetComponent<GA_Manager>();
        this.windForce = Vector3.zero;
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

        // Angle
        Vector2 my_forward_vec = new Vector2(this.transform.forward.x, this.transform.forward.z);
        Vector2 checkpoint_pos_vec = new Vector2((this.checkpoints[0] - this.transform.position).x, (this.checkpoints[0] - this.transform.position).z);
        float angle = Vector2.SignedAngle(my_forward_vec.normalized, checkpoint_pos_vec.normalized) / 180f;

        float normalized_speed = this._rigidbody.linearVelocity.magnitude / this.max_speed;
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
        float current_speed = this._rigidbody.linearVelocity.magnitude;
        this.grounded = this.grounded || Physics.Raycast(this.transform.position, -Vector3.up, 0.8f);

        if (!this.grounded)
        {
            this.transform.position -= this.transform.up * 0.5f;
            return;
        }
        if (this._rigidbody.linearVelocity.magnitude > 0)
        {
            float steering_force = steering * Time.fixedDeltaTime * 100f;
            this.transform.rotation = Quaternion.Euler(new Vector3(0, steering_force, 0) + this.transform.rotation.eulerAngles);
            this._rigidbody.linearVelocity = current_speed * this.transform.forward;
        }
        if (acceleration < -0.2f || acceleration > 0.2f)
        {
            float speed = current_speed;
            speed += acceleration * this.acceleration_rate * Time.fixedDeltaTime;
            speed = Mathf.Min(speed, this.max_speed);
            this._rigidbody.linearVelocity = this.transform.forward * speed;
        }
        //this._rigidbody.linearVelocity = Vector3.ClampMagnitude(this._rigidbody.linearVelocity, this.max_speed);
        this.transform.position += this.windForce * Time.fixedDeltaTime * 5f;
    }


    void OnTriggerEnter(Collider other)
    {
        if (!this.canMove)
        {
            return;
        }
        else if (other.tag.Equals("Wind"))
        {
            this.windForce = other.transform.forward;
        }
        else if (other.tag.Equals("Wall"))
        {
            this.StopMoving();
        }
        else if (other.tag.Equals("Checkpoint"))
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

    void OnTriggerExit(Collider other)
    {
        if (other.tag.Equals("Wind"))
        {
            this.windForce = Vector3.zero;
        }
    }


    public void StopMoving()
    {
        this.canMove = false;
        this._rigidbody.linearVelocity = Vector3.zero;
        this._gaManager.nb_cars_alives -= 1;
    }

    public void SetSkin(bool car_is_first)
    {
        this.transform.Find("YellowSkin").gameObject.SetActive(car_is_first);
        this.transform.Find("GreySkin").gameObject.SetActive(!car_is_first);
    }
}
