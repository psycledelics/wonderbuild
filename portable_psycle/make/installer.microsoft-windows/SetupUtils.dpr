// Install helper utility (C) Haralabos Michael 2002

program SetupUtils;

uses
  Windows, SysUtils, Registry;

var
  Reg: TRegistry;
begin
  if ParamCount > 0 then
  case StrToInt(ParamStr(1)) of
    1: MoveFileEx(PChar(ParamStr(2)), PChar(ParamStr(3)), MOVEFILE_REPLACE_EXISTING);
    2: begin
         Reg := TRegistry.Create;

         with Reg do
         begin
           RootKey := HKEY_CURRENT_USER;
           DeleteKey('aas');
         end;

         FreeAndNil(Reg);
       end;
  end;
end.
