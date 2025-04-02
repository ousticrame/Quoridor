using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;

public class GA_Manager : MonoBehaviour
{
    [SerializeField] int NB_START_POPULATION;
    [SerializeField] int NB_DADS;
    [SerializeField] bool LOAD_NN;
    [SerializeField] string SAVE_FILE;
    [SerializeField] float SIMULATION_SPEED;
    [SerializeField] GameObject drone_prefab;
    
    [HideInInspector] public int nb_drones_alives; // this is decremented by drones when they die
    [SerializeField] int max_nb_epochs;
    [SerializeField] int max_ticks_for_epoch;
    private int nb_epochs;
    private int ticks;
    

    List<DroneController> drones;
    private Vector3 spawnPoint;

    private List<Vector3> checkpointsPositions;
    
    private NN debug_nn;

    private void Start()
    {
        // FRAME RATE & CO
        //Time.fixedDeltaTime = 0.02f;
        //Application.targetFrameRate = 60;
        Time.timeScale = this.SIMULATION_SPEED;
        ////////////////////
        this.GetSpawnPoint();
        this.GetCheckpoints();
        this.InstantiateStartDrones();
        this.ticks = 0;
    }

    private void FixedUpdate()
    {
        if (this.nb_drones_alives <= 0 || this.ticks >= this.max_ticks_for_epoch)
        {
            this.ticks = 0;
            this.InstantiateNewGenDrones();
            return;
        }
        foreach (var drone in this.drones)
        {
            drone.Move();
        }
        this.ticks++;

        // DEBUG DEBUG DEBUG
        /*if (this.nb_epochs == 10)
        {
            this.nb_dads = 1;
            this.NB_POPULATION = 1;
        }*/
    }



    // EPOCH METHODS
    private void InstantiateNewGenDrones()
    {
        List<NN> dads = this.getBestNetworks();
        List<NN> new_networks = this.getNewNetworks(dads);
        this.CleanLastEpoch();

        for (int i = 0; i < new_networks.Count; i++)
        {
            GameObject drone = Instantiate(this.drone_prefab, this.spawnPoint, Quaternion.identity);
            drone.GetComponent<DroneController>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            drone.GetComponent<DroneController>().network = new_networks[i].DeepCopy();
            this.drones.Add(drone.GetComponent<DroneController>());
        }
        this.nb_drones_alives = new_networks.Count;
        Debug.Log(new_networks.Count);
        this.ticks = 0;
        Time.timeScale = this.SIMULATION_SPEED;
    }

    private List<NN> getNewNetworks(List<NN> dads)
    {
        List<NN> new_networks = new List<NN>();
        new_networks.AddRange(dads);
        new_networks.AddRange(GA_Algorithms.two_parents_mutation_top_n_dads(dads, 10, 0.2f, 0.2f));
        new_networks.AddRange(GA_Algorithms.basic_mutation(dads, 0.2f, 0.2f));
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

        this.drones = this.drones.OrderByDescending(x => x.score).ToList();
        if (this.drones[0].score == this.checkpointsPositions.Count) // they already completed the track, so now we go fast boyy
        {
            this.drones = this.drones.OrderByDescending(x => x.score).ThenBy(x => x.ticksTaken).ToList();
        }
        NN_Utilities.SaveNN(this.SAVE_FILE, this.drones[0].network);
        Debug.Log($"Epoch: {this.nb_epochs++}, best_score: {this.drones[0].score}");
        List<NN> result = new List<NN>();
        for (int i = 0; i < this.NB_DADS; i++)
        {
            result.Add(this.drones[i].network.DeepCopy());
        }
        return result;
    }

    private void CleanLastEpoch()
    {
        foreach(DroneController drone in this.drones)
        {
            Destroy(drone.gameObject);
        }
        this.drones.Clear();
    }


    // START METHODS
    private void InstantiateStartDrones()
    {
        this.drones = new List<DroneController>();
        for (int i = 0; i < this.NB_START_POPULATION; i++)
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
                drone.GetComponent<DroneController>().network.AddLayer(13, 16, ActivationMethod.ReLU);
                drone.GetComponent<DroneController>().network.AddLayer(16, 8, ActivationMethod.ReLU);
                drone.GetComponent<DroneController>().network.AddLayer(8, 3, ActivationMethod.Sigmoid);
                drone.GetComponent<DroneController>().network.Mutate(1f, 1f);
            }
            this.drones.Add(drone.GetComponent<DroneController>());
        }
        this.nb_drones_alives = this.NB_START_POPULATION;
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
