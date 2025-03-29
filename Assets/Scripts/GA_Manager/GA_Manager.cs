using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

public class GA_Manager : MonoBehaviour
{
    [SerializeField] GameObject drone_prefab;
    [SerializeField] int nb_population;
    [SerializeField] int nb_epochs;
    [SerializeField] int nb_dads;

    List<DroneController> drones;

    private void Start()
    {
        this.InstantiateStartDrones();
    }

    private void FixedUpdate()
    {
        foreach (DroneController drone in this.drones)
        {
            drone.Move();
        }
    }





    private void InstantiateStartDrones()
    {
        this.drones = new List<DroneController>();
        for (int i = 0; i < this.nb_population; i++)
        {
            GameObject drone = Instantiate(this.drone_prefab, new Vector3(0, 0, 0), Quaternion.identity);
            drone.GetComponent<DroneController>().network = new NN();
            drone.GetComponent<DroneController>().network.Mutate(1f, 1f);
            drone.GetComponent<DroneController>().network.AddLayer(18, 4, ActivationMethod.ReLU); // TODO: change 18 to the real number
            drone.GetComponent<DroneController>().network.AddLayer(4, 4, ActivationMethod.ReLU);
            drone.GetComponent<DroneController>().network.AddLayer(4, 3, ActivationMethod.Sigmoid);
            this.drones.Add(drone.GetComponent<DroneController>());
        }
    }
}
