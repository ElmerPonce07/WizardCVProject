using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class SpellReceiver : MonoBehaviour
{
    UdpClient client;
    public int port = 5005; // must match your Python port
    public Animator anim;

    void Start()
    {
        client = new UdpClient(port);
        client.BeginReceive(ReceiveCallback, null);
    }

    void ReceiveCallback(IAsyncResult ar)
    {
        IPEndPoint ep = new IPEndPoint(IPAddress.Any, port);
        byte[] data = client.EndReceive(ar, ref ep);
        string message = Encoding.UTF8.GetString(data).Trim();

        Debug.Log("Received: " + message);

        if (message == "Fire") anim.SetTrigger("CastFire");
        else if (message == "Water") anim.SetTrigger("CastWater");
        else if (message == "Earth") anim.SetTrigger("CastEarth");
        else if (message == "PlayerDead") Debug.Log("💀 Player lost!");
        else if (message == "MageDead") Debug.Log("🏆 Player won!");

        client.BeginReceive(ReceiveCallback, null); // keep listening
    }

    void OnApplicationQuit()
    {
        if (client != null) client.Close();
    }
}
