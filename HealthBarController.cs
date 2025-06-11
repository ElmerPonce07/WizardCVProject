using UnityEngine;
using UnityEngine.UI;

public class HealthBarController : MonoBehaviour
{
    public Slider playerSlider;
    public Slider mageSlider;

    public void SetPlayerHealth(float value)
    {
        playerSlider.value = value;
    }

    public void SetMageHealth(float value)
    {
        mageSlider.value = value;
    }
}
