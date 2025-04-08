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

    private float speeds_sum;
    private float nb_speeds;
    private float maxSpeed;

    void Awake()
    {
        this.speeds_sum = 0;
        this.nb_speeds = 0;
        this.maxSpeed = -1;
    }

    private void FixedUpdate()
    {
        if (this.toFollow != null && this.toFollow.GetComponent<CarController>().canMove)
        {
            this.transform.position = this.toFollow.transform.position + new Vector3(0, 50, 0);
            this.transform.LookAt(this.toFollow.transform);
            float speed = this.toFollow.GetComponent<Rigidbody>().linearVelocity.magnitude;
            speedText.text = "Speed: " + speed.ToString("0.##");
            if (speed > this.maxSpeed)
            {
                this.maxSpeed = speed;
                this.maxSpeedText.text = "Max Speed: " + speed.ToString("0.##");
            }
            this.speeds_sum += speed;
            this.nb_speeds++;
            this.meanSpeedText.text = "Avg Speed: " + (this.speeds_sum / this.nb_speeds).ToString("0.##");
        }
    }

    public void resetToFollow()
    {
        this.speeds_sum = 0;
        this.nb_speeds = 0;
        this.toFollow = null;
        this.maxSpeed = -1;
    }
}
