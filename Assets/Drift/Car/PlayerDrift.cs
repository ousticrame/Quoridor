using System.Collections.Generic;
using UnityEngine;

public class PlayerDrift : MonoBehaviour
{
    public int ticksTaken = 0;
    public bool canMove;
    private Rigidbody _rigidbody;
    private bool grounded = false;

    // SPEED VARS
    public float current_speed;
    [SerializeField] private float max_speed;
    [SerializeField] private float acceleration_rate;

    void Awake()
    {
        this.canMove = true;
        this.ticksTaken = 0;
        this.current_speed = 0f;
        this._rigidbody = this.GetComponent<Rigidbody>();
        Time.timeScale = 2;
    }

    public void FixedUpdate()
    {
        float steering = 0;
        if (Input.GetKey(KeyCode.RightArrow))
        {
            steering += 1;
            Debug.Log("right");
        }
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            steering -= 1;
            Debug.Log("left");
        }
        float acceleration = 1f;//outputs[1];
        this.grounded = true;//this.grounded;
        if (!this.grounded)
        {
            //this._rigidbody.linearVelocity = this.transform.up * -0.5f;
            this.transform.position -= this.transform.up * 0.5f;
            return;
        }
        if (true /*this._rigidbody.linearVelocity.x > 0 || this._rigidbody.linearVelocity.z > 0*/)
        {
            this.transform.rotation = Quaternion.Euler(new Vector3(0, steering * Time.fixedDeltaTime * 300f, 0) + this.transform.rotation.eulerAngles);
        }
        if (acceleration < -0.2f || acceleration > 0.2f)
        {
            this._rigidbody.linearVelocity += this.transform.forward * acceleration * this.acceleration_rate * Time.fixedDeltaTime;
        }
        /*float x = Mathf.Clamp(localVelocity.x, 0, this.max_speed);
        float z = Mathf.Clamp(localVelocity.z, 0, this.max_speed);*/
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
        }
    }

    public void StopMoving()
    {
        this.canMove = false;
        this._rigidbody.linearVelocity = Vector3.zero;
    }
}
