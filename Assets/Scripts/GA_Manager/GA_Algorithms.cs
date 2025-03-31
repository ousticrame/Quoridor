using System.Collections.Generic;
using NUnit.Framework.Interfaces;
using UnityEngine;

public static class GA_Algorithms
{
    public static List<NN> basic_mutation(List<NN> dads, int nb_children, float mutation_proba, float mutation_amount)
    {
        List<NN> result = new List<NN>();
        for (int i = 0; i < nb_children; i++)
        {
            NN child = dads[i % dads.Count].DeepCopy();
            child.Mutate(mutation_proba, mutation_amount);
            result.Add(child);
        }
        return result;
    }

    public static List<NN> two_parents_mutation(List<NN> dads, float mutation_proba, float mutation_amount)
    {
        List<NN> result = new List<NN>();
        for (int i = 0; i < dads.Count; i++)
        {
            for (int j = i + 1; j < dads.Count; j++)
            {
                NN dad1 = dads[i].DeepCopy();
                NN dad2 = dads[j].DeepCopy();
                // TODO: write a function to do the average between n neural networks and then merge them
                // TODO: then mutate the children -> add the non mutated and the mutated child
                // result.Add(dad1 average with dad2)
                // result.Add(dad1 average with dad2, but mutated)
            }
        }
        return result;
    }

    public static NN average_child(List<NN> dads)
    {
        // TODO: do the averaged child amongst all dads and return it
        return new NN();
    }
}
