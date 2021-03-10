//----------------------------------------------
// Custom Support 
// Size must be 1x1x1 
// Tested in Cura with Support Size : 30
// Recommanded Infill support > 12%
//----------------------------------------------
$fn=30;

translate([-0.5,-0.5,-1.0]) 
union() {
    translate([0.5,0.55,0.0]) rotate([90, 0, 0]) {
			linear_extrude(height=0.1) {
				polygon(points=[[-0.62,0],[-1.20,0],[-1,0.4],[-0.05,1],[0.05,1],[0.05,0.95],[-0.35,0.5]], convexity=1);
			}
		}
    translate([-0.2,0.5,0.0]) rotate([90, 0, 90]) {
			linear_extrude(height=0.1) {
				polygon(points=[[-0.25,0],[0.25,0],[0.05,0.5],[-0.05,0.5]], convexity=1);
			}        
    }
}
