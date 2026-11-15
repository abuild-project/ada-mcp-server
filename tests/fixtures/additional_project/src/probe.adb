package body Probe is
   procedure Increment (Item : in out Integer) is
   begin
      Item := Item + 1;
   end Increment;

   function Combine (Left : Integer; Right : Integer) return Integer is
   begin
      return Left + Right;
   end Combine;
end Probe;
