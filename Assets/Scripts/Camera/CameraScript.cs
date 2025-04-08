using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

public class CameraScript : MonoBehaviour
{
    public GameObject toFollow;
    [SerializeField] Text speedText;
    [SerializeField] Text meanSpeedText;
    [SerializeField] Text maxSpeedText;

    private List<float> speeds;
    private float maxSpeed;

    void Awake()
    {
        this.speeds = new List<float>();
        this.maxSpeed = -1;
    }

    private void FixedUpdate()
    {
        if (this.toFollow != null && this.toFollow.GetComponent<CarController>().canMove)
        {
            this.transform.position = this.toFollow.transform.position + new Vector3(0, 50, 0);
            this.transform.LookAt(this.toFollow.transform);
            float speed = this.toFollow.GetComponent<Rigidbody>().linearVelocity.magnitude;
            speedText.text = "Speed: " + speed.ToString() + "km/h";
            if (speed > this.maxSpeed)
            {
                this.maxSpeed = speed;
                this.maxSpeedText.text = "Max Speed: " + speed.ToString() + "km/h";
            }
            this.speeds.Add(speed);
            this.meanSpeedText.text = "Average Speed: " + this.speeds.Average().ToString() + "km/h";
        }
    }

    public void resetToFollow()
    {
        this.speeds.Clear();
        this.toFollow = null;
        this.maxSpeed = -1;
    }
}
