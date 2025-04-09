using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

public class GA_ManagerDrift : MonoBehaviour
{
    [SerializeField] int NB_START_POPULATION;
    [SerializeField] int NB_DADS;
    [SerializeField] bool LOAD_NN;
    [SerializeField] string SAVE_FILE;
    [SerializeField] float SIMULATION_SPEED;
    [SerializeField] GameObject car_prefab;
    
    [HideInInspector] public int nb_cars_alives; // this is decremented by cars when they die
    [SerializeField] int max_nb_epochs;
    [SerializeField] int max_ticks_for_epoch;
    private int nb_epochs;
    private int ticks;

    private CameraScriptDrift cameraScript;
    

    List<CarControllerDrift> cars;
    private Transform spawnPoint;

    private List<Vector3> checkpointsPositions;
    
    private NN debug_nn;

    private void Start()
    {
        // FRAME RATE & CO
        //Time.fixedDeltaTime = 0.02f;
        //Application.targetFrameRate = 60;
        Time.timeScale = this.SIMULATION_SPEED;
        this.cameraScript = GameObject.Find("Main Camera").GetComponent<CameraScriptDrift>();
        ////////////////////
        this.GetSpawnPoint();
        this.GetCheckpoints();
        this.InstantiateStartCars();
        this.ticks = 0;
    }

    private void FixedUpdate()
    {
        if (this.nb_cars_alives <= 0 || this.ticks >= this.max_ticks_for_epoch)
        {
            this.ticks = 0;
            this.InstantiateNewGenCars();
            return;
        }
        foreach (var car in this.cars)
        {
            car.Move();
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
    private void InstantiateNewGenCars()
    {
        this.cameraScript.resetToFollow();
        List<NN> dads = this.getBestNetworks();
        List<NN> new_networks = this.getNewNetworks(dads);
        this.CleanLastEpoch();

        for (int i = 0; i < new_networks.Count; i++)
        {
            GameObject car = Instantiate(this.car_prefab, this.spawnPoint.position, this.spawnPoint.rotation);
            car.GetComponent<CarControllerDrift>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            car.GetComponent<CarControllerDrift>().network = new_networks[i].DeepCopy();
            this.cars.Add(car.GetComponent<CarControllerDrift>());
        }
        this.cameraScript.toFollow = this.cars[0].gameObject;
        this.nb_cars_alives = new_networks.Count;
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
        foreach(CarControllerDrift car in this.cars)
        {
            if (car.canMove)
            {
                car.StopMoving();
            }
        }

        this.cars = this.cars.OrderByDescending(x => x.score).ToList();
        if (this.cars[0].score == this.checkpointsPositions.Count) // they already completed the track, so now we go fast boyy
        {
            this.cars = this.cars.OrderByDescending(x => x.score).ThenBy(x => x.ticksTaken).ToList();
        }
        NN_Utilities.SaveNN(this.SAVE_FILE, this.cars[0].network);
        List<NN> result = new List<NN>();
        for (int i = 0; i < this.NB_DADS; i++)
        {
            result.Add(this.cars[i].network.DeepCopy());
        }
        return result;
    }

    private void CleanLastEpoch()
    {
        foreach(CarControllerDrift car in this.cars)
        {
            Destroy(car.gameObject);
        }
        this.cars.Clear();
    }


    // START METHODS
    private void InstantiateStartCars()
    {
        this.cars = new List<CarControllerDrift>();
        for (int i = 0; i < this.NB_START_POPULATION; i++)
        {
            GameObject car = Instantiate(this.car_prefab, this.spawnPoint.position, this.spawnPoint.rotation);
            car.GetComponent<CarControllerDrift>().checkpoints = this.checkpointsPositions.ConvertAll(x => new Vector3(x.x, x.y, x.z)); // deep copy
            if (this.LOAD_NN)
            {
                car.GetComponent<CarControllerDrift>().network = NN_Utilities.LoadNN(this.SAVE_FILE);
            }
            else
            {
                car.GetComponent<CarControllerDrift>().network = new NN();
                car.GetComponent<CarControllerDrift>().network.AddLayer(9, 7, ActivationMethod.ReLU);
                car.GetComponent<CarControllerDrift>().network.AddLayer(7, 4, ActivationMethod.ReLU);
                car.GetComponent<CarControllerDrift>().network.AddLayer(4, 2, ActivationMethod.Sigmoid);
                car.GetComponent<CarControllerDrift>().network.Mutate(1f, 1f);
            }
            this.cars.Add(car.GetComponent<CarControllerDrift>());
        }
        this.nb_cars_alives = this.NB_START_POPULATION;
        this.cameraScript.toFollow = this.cars[0].gameObject;
    }

    private void GetSpawnPoint()
    {
        this.spawnPoint = GameObject.Find("SpawnPoint").transform;
    }

    private void GetCheckpoints()
    {
        GameObject checkpoints = GameObject.Find("RoadManager");
        this.checkpointsPositions = checkpoints.GetComponent<SplineRoadCreatorDrift>().checkpoints.ConvertAll(x => new Vector3(x.x, x.y, x.z));
    }

    public void LoadMainMenu()
    {
        SceneManager.LoadScene("Menu");
    }
}
