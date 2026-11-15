package Probe is
   -- Declarations move and change in the warm state.

   procedure Advance (Item : in out Natural);
   function Merge (Left : Natural; Right : Natural; Extra : Natural) return Natural;
end Probe;
