....
if (isset($_POST['cfg_id'])) {  //
 $ovpncfg_id = $_POST['cfg_id']; // Here cfg_id is used without sanitization
 $ovpncfg_files = pathinfo(RASPI_OPENVPN_CLIENT_LOGIN, PATHINFO_DIRNAME).'/'.$ovpncfg_id.'_*.conf'; // then it's appended to a path
 exec("sudo rm $ovpncfg_files", $return); // exec sudo is called on the path