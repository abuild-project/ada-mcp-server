package body Probe is
   -- Bodies move and change in the warm state.

   procedure Advance (Item : in out Natural) is
   begin
      Item := Item + 1;
   end Advance;

   function Merge (Left : Natural; Right : Natural; Extra : Natural) return Natural is
   begin
      return Left + Right + Extra;
   end Merge;
end Probe;
