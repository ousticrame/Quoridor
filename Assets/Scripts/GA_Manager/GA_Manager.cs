using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;

public class GA_Manager : MonoBehaviour
{
    [SerializeField] bool LOAD_NN;
    [SerializeField] string SAVE_FILE;
    [SerializeField] float SIMULATION_SPEED;
    [SerializeField] GameObject drone_prefab;
    [SerializeField] int NB_POPULATION;
    [HideInInspector] public int nb_drones_alives; // this is decremented by drones when they die
    [SerializeField] int max_nb_epochs;
    [SerializeField] int max_ticks_for_epoch;
    private int nb_epochs;
    private int ticks;
    [SerializeField] int nb_dads;

    List<DroneController> drones;
    private Vector3 spawnPoint;

    private List<Vector3> checkpointsPositions;
    

    private void Start()
    {
        // FRAME RATE & CO
        QualitySettings.vSyncCount = 0;
        Application.targetFrameRate = 60;
        UnityEngine.Random.InitState(12345);
        System.Random rand = new System.Random(12345);
        Time.timeScale = this.SIMULATION_SPEED;
        ////////////////////
        this.GetSpawnPoint();
        this.GetCheckpoints();
        this.InstantiateStartDrones();
        this.ticks = 0;
    }

    private void FixedUpdate()
    {
        if (this.nb_drones_alives <= 0)
        {
            this.InstantiateNewGenDrones();
            return;
        }
    }



    // EPOCH METHODS
    private void InstantiateNewGenDrones()
    {
        List<NN> dads = this.getBestNetworks();
        NN_Utilities.SaveNN(this.SAVE_FILE, dads[0]);
        List<NN> new_networks = this.getNewNetworks(dads);
        this.CleanLastEpoch();
        this.drones = new List<DroneController>();
        for (int i = 0; i < this.NB_POPULATION; i++)
        {
            GameObject drone = Instantiate(this.drone_prefab, this.spawnPoint, Quaternion.identity);
            drone.GetComponent<DroneController>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            drone.GetComponent<DroneController>().network = new_networks[i];
            this.drones.Add(drone.GetComponent<DroneController>());
        }
        this.nb_drones_alives = this.NB_POPULATION;
        this.ticks = 0;
    }

    private List<NN> getNewNetworks(List<NN> dads)
    {
        List<NN> new_networks = new List<NN>();
        new_networks.AddRange(dads.ConvertAll(x => x.DeepCopy()));
        for (int i = 0; i < this.NB_POPULATION - dads.Count; i++)
        {
            NN mutated = dads[i % dads.Count].DeepCopy();
            mutated.Mutate(0.2f, 0.5f);
            new_networks.Add(mutated);
        }
        return new_networks;
    }

    private List<NN> getBestNetworks()
    {
        foreach(DroneController drone in this.drones)
        {
            if (drone.canMove)
            {
                drone.StopMoving();
            }
        }
        this.drones = this.drones.OrderByDescending(x => x.score).ThenBy(x => x.ticksTaken).ToList();
        Debug.Log(this.drones[0].score);
        List<NN> best_networks = this.drones.GetRange(0, this.nb_dads).ConvertAll(x => x.network).ToList();
        return best_networks;
    }

    private void CleanLastEpoch()
    {
        foreach(DroneController drone in this.drones)
        {
            Destroy(drone.gameObject);
        }
    }


    // START METHODS
    private void InstantiateStartDrones()
    {
        this.drones = new List<DroneController>();
        for (int i = 0; i < this.NB_POPULATION; i++)
        {
            GameObject drone = Instantiate(this.drone_prefab, this.spawnPoint, Quaternion.identity);
            drone.GetComponent<DroneController>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            if (this.LOAD_NN)
            {
                drone.GetComponent<DroneController>().network = NN_Utilities.LoadNN(this.SAVE_FILE);
            }
            else
            {
                drone.GetComponent<DroneController>().network = new NN();
                drone.GetComponent<DroneController>().network.AddLayer(6, 4, ActivationMethod.ReLU);
                drone.GetComponent<DroneController>().network.AddLayer(4, 4, ActivationMethod.ReLU);
                drone.GetComponent<DroneController>().network.AddLayer(4, 3, ActivationMethod.Sigmoid);
                drone.GetComponent<DroneController>().network.Mutate(1f, 1f);
            }
            this.drones.Add(drone.GetComponent<DroneController>());
        }
        this.nb_drones_alives = this.NB_POPULATION;
    }

    private void GetSpawnPoint()
    {
        this.spawnPoint = GameObject.Find("SpawnPoint").transform.position;
    }

    private void GetCheckpoints()
    {
        GameObject checkpoints = GameObject.Find("Checkpoints");
        this.checkpointsPositions = new List<Vector3>();
        for (int i = 0; i < checkpoints.transform.childCount; i++)
        {
            this.checkpointsPositions.Add(checkpoints.transform.GetChild(i).transform.position);
        }
        /*foreach (var a in this.checkpointsPositions)
        {
            Debug.Log(a);
        }*/
    }
}
