using Microsoft.AspNetCore.Mvc;

public record DynamicVessel(int TimeStamp, string? Status);

[ApiController]
[Route("api/[controller]")]
public class DynamicVesselController: ControllerBase
{
    [HttpGet] //route api/dynamicvessel
    public ActionResult<DynamicVessel[]> Get()
    {
        var data = new[]
        {
            new DynamicVessel(14949,"test"),
            new DynamicVessel(15,"test")
        };
        return Ok(data);
    }

}