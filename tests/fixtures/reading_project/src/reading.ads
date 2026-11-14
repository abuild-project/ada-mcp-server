package Reading is
   type Counter is record
      Value : Integer;
   end record;
   procedure Reading_Probe_Increment (Item : in out Counter);
end Reading;
