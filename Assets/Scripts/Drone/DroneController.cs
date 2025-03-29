using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Rendering;

public class DroneController : MonoBehaviour
{
    private RayCastSystem rcs;
    public NN network;
    private int ticksTaken = 0;

    void Awake()
    {
        this.ticksTaken = 0;
        this.rcs = this.gameObject.GetComponent<RayCastSystem>();
    }

    public void Move()
    {
        this.ticksTaken++;
        float[] inputs = this.BuildInputs();
        float[] outputs = this.network.Forward(inputs);
        this.ProcessOutputs(outputs);
    }

    public float[] BuildInputs()
    {
        float[] raycasts = this.rcs.getDistances();
        float[] position = {this.transform.position.x, this.transform.position.y, this.transform.position.z};
        float[] target_position = {}; // TODO: pass next checkpoint here


        List<float> inputs = new List<float>();
        inputs.AddRange(raycasts);
        inputs.AddRange(position);
        inputs.AddRange(target_position);

        return inputs.ToArray();
    }

    public void ProcessOutputs(float[] outputs)
    {
        float y_up = outputs[0];
        float y_rotation = outputs[1];
        float z_forward = outputs[2];
        this.transform.rotation = Quaternion.Euler(new Vector3(0, y_rotation, 0) * 2f + this.transform.rotation.eulerAngles);
        this.GetComponent<Rigidbody>().linearVelocity = this.transform.forward * z_forward * 5f + this.transform.up * y_up;
    }
}
