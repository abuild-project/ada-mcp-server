package body Reading is
   procedure Reading_Probe_Increment (Item : in out Counter) is
   begin
      Item.Value := Item.Value + 1;
   end Reading_Probe_Increment;
end Reading;
