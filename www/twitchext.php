<?php
require('twitchext-secrets.php');

$conn = new mysqli($mysql_host, $mysql_user, $mysql_pass, $mysql_db);
if ($conn->connect_error) mysqlerr($conn, "connect err");

define('STATUS_INCOMPLETE', 1);
define('STATUS_READY', 2);
define('STATUS_COMPLETE', 3);

define("ER_DUP_ENTRY", 1062);

define("EXPIRY_TIMEOUT", 3600);
define("OTP_LENGTH", 7);
define("JWT_EXPIRY", 86400);
define("TOKEN_LENGTH", 64);

function main() {
	if (!empty($_REQUEST['login'])) {
		new_user();
	} else if (!empty($_REQUEST['code']) && !empty($_REQUEST['state'])) {
		post_auth();
	} else if (!empty($_REQUEST['otp']) && !empty($_REQUEST['code'])) {
		resolve_otp();
	}	else if (!empty($_REQUEST['token'])) {
		resolve_token();
	} else {
		die("no mode");
	}
}

function mysqlerr($obj, $msg) {
	global $mysql_dbg;
	if ($mysql_dbg) {
		$msg = "$msg - " . $obj->error;
	}
	die($msg);
}

function new_user() {
	// Step 1: start new signon
	global $conn, $client_id, $redirect_uri;
	$nonce = $_REQUEST['login'];

	if (strlen($nonce) != TOKEN_LENGTH)
		die("Nonce length must be " . TOKEN_LENGTH);
	// store this login step in the staging table
	$qry = $conn->prepare("INSERT INTO oauth_session(nonce, status, created) VALUES(?,?,?)") or mysqlerr($conn, "prepare err");
	$status = STATUS_INCOMPLETE; // for some reason it has to be a real var??? php why
	$now = gmdate('Y-m-d H:i:s');
	$qry->bind_param('sis', $nonce, $status, $now) or mysqlerr($qry, "bind err");
	if (!$qry->execute()) {
		if ($qry->errno == ER_DUP_ENTRY)
			die("Nonce already used");
		else
			mysqlerr($qry, "execute err");
	}
?>
<!DOCTYPE html>
<title>Log in to Twitch</title>
<form action="https://id.twitch.tv/oauth2/authorize" method="GET" id="frm">
<input type="hidden" name="client_id", value="<?=htmlspecialchars($client_id)?>">
<input type="hidden" name="redirect_uri", value="<?=htmlspecialchars($redirect_uri)?>">
<input type="hidden" name="response_type", value="code">
<input type="hidden" name="scope", value="">
<input type="hidden" name="force_verify", value="true">
<input type="hidden" name="state", value="<?=htmlspecialchars($nonce)?>">
</form>
<script>document.getElementById("frm").submit();</script>
<?php
}

function post_auth() {
	// Step 2: User has approved on Twitch, complete login process
	global $conn, $client_id, $client_secret, $redirect_uri;
	$nonce = $_REQUEST['state'];
	$code = $_REQUEST['code'];

	// Check this is a code we're expecting a login for
	// ... goddamn this is a lot of faffing about to run a single query
	$qry = $conn->prepare("SELECT COUNT(*) FROM oauth_session WHERE nonce=? AND status=? AND created>?") or mysqlerr($conn, "prepare err");
	$status = STATUS_INCOMPLETE;
	$cutoff = gmdate('Y-m-d H:i:s', time() - EXPIRY_TIMEOUT);
	$qry->bind_param('sis', $nonce, $status, $cutoff) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");
	$qry->bind_result($count) or mysqlerr($qry, "bindres err");
	$qry->fetch() or mysqlerr($qry, "fetch err");
	$qry->close();

	if ($count <= 0) die("Unrecognised code - may have timed out, please try again");

	// Contact Twitch to get login token
	$body = http_build_query([
		'client_id'=>$client_id,
		'client_secret'=>$client_secret,
		'code'=>$code,
		'grant_type'=>'authorization_code',
		'redirect_uri'=>$redirect_uri,
	]);
	$ctx = stream_context_create(["http"=>[
		"header"=>[
			"Client-ID: $client_id",
			"Content-type: application/x-www-form-urlencoded",
		],
		"method"=>"POST",
		"content"=>$body,
	]]);
	$data = file_get_contents("https://id.twitch.tv/oauth2/token", FALSE, $ctx) or die("Error contacting Twitch");
	$data = json_decode($data) or die("Error decoding Twitch response");
	$token = $data->access_token;

	// Use login token to get identity of the user
	$ctx = stream_context_create(["http"=>[
		"header"=>[
			"Client-ID: $client_id",
			"Authorization: Bearer $token",
		],
		"method"=>"GET",
	]]);
	$data = file_get_contents("https://api.twitch.tv/helix/users", FALSE, $ctx) or die("Error getting user details");
	$data = json_decode($data) or die("Error decoding user details");
	count($data->data) or die("Error empty user details");
	$user = $data->data[0];

	// Create an authentication token, store the user details in the database
	$token = gen_token();
	$qry = $conn->prepare("INSERT INTO login_token(token, userid, display_name, created, lastaccessed) values(?,?,?,?,?)") or mysqlerr($conn, "prepare err");
	$now = gmdate('Y-m-d H:i:s');
	$qry->bind_param('sssss', $token, $user->id, $user->display_name, $now, $now) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");

	// Generate OTP for final step, link with token
	$otp = gen_otp();
	$qry = $conn->prepare("UPDATE oauth_session SET status=?, token=?, otp=?, created=? WHERE nonce=?") or mysqlerr($conn, "prepare err");
	$now = gmdate('Y-m-d H:i:s');
	$status = STATUS_READY;
	$qry->bind_param('issss', $status, $token, $otp, $now, $nonce) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");

	// Provide OTP to user
?>
<!DOCTYPE html>
<style>
	body { text-align: center; font: 100% sans-serif; }
	.username { font-weight: bold; }
	.code { font-size: 200%; font-weight: bold; }
</style>
<p>You are logged in as: <span class="username"><?=htmlspecialchars($user->display_name)?></span>
<p>Return to the application, and enter this code</p>
<p class="code"><?=htmlspecialchars($otp)?></p>
<?php
}

function resolve_otp() {
	// Step 3: Client application uses OTP to get login token
	global $conn;
	$nonce = $_REQUEST['code'];
	$otp = $_REQUEST['otp'];

	// Check this is the correct OTP
	$qry = $conn->prepare("SELECT token FROM oauth_session WHERE nonce=? AND otp=? AND status=? AND created>?") or mysqlerr($conn, "prepare err");
	$status = STATUS_READY;
	$cutoff = gmdate('Y-m-d H:i:s', time() - EXPIRY_TIMEOUT);
	$qry->bind_param('ssis', $nonce, $otp, $status, $cutoff) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");
	$qry->bind_result($token) or mysqlerr($qry, "bindres err");
	$ret = $qry->fetch();
	// why do you have to be such a butt, PHP
	if ($ret === NULL) {
		header("Content-type: application/json");
		die(json_encode(["error"=>"Incorrect or expired code, please try again"]));
	}
	else if ($ret === FALSE)
		mysqlerr($qry, "fetch err");
	$qry->close();

	// mark the token as active
	$otp = gen_otp();
	$qry = $conn->prepare("UPDATE oauth_session SET status=?, otp=NULL WHERE nonce=?") or mysqlerr($conn, "prepare err");
	$status = STATUS_COMPLETE;
	$qry->bind_param('is', $status, $nonce) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");

	// return token to app
	header("Content-type: application/json");
	print json_encode([
		"token"=>$token,
	]);
}

function resolve_token() {
	// Step 4: Use token to get JWT and user details
	global $conn;
	$token = $_REQUEST['token'];

	$qry = $conn->prepare("SELECT userid, display_name FROM login_token WHERE token=?") or mysqlerr($conn, "prepare err");
	$qry->bind_param('s', $token) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");
	$qry->bind_result($userid, $display_name) or mysqlerr($qry, "bindres err");
	$ret = $qry->fetch();
	if ($ret === NULL) {
		header("Content-type: application/json");
		die(json_encode(["error"=>"Unrecognised token, please log in again"]));
	}
	else if ($ret === FALSE)
		mysqlerr($qry, "fetch err");
	$qry->close();

	$qry = $conn->prepare("UPDATE login_token SET lastaccessed=? WHERE token=?") or mysqlerr($conn, "prepare err");
	$now = gmdate('Y-m-d H:i:s');
	$qry->bind_param('is', $token, $now) or mysqlerr($qry, "bind err");
	$qry->execute() or mysqlerr($qry, "execute err");

	$jwt = generate_jwt($userid);
	header("Content-type: application/json");
	print json_encode([
		"userid"=>$userid,
		"name"=>$display_name,
		"jwt"=>$jwt['token'],
		"expiry"=>$jwt['expiry'],
	]);
}

function gen_token() {
	// Returns a TOKEN_LENGTH-character alnum (almost) string
	// using the CSPRNG in PHP7
	return base64_encode(random_bytes(3 * TOKEN_LENGTH / 4));
}

function gen_otp() {
	// Returns a 7-digit number
	// using CSPRNG in PHP7
	$s = '';
	for ($i = 0; $i < OTP_LENGTH; $i++)
		$s .= random_int(0, 9);
	return $s;
}

function urlsafeB64Encode($input)
{
	return str_replace('=', '', strtr(base64_encode($input), '+/', '-_'));
}


function generate_jwt($userid) {
	global $ext_secret;

	$expiry = time() + EXPIRY_TIMEOUT;
	$header = ["typ"=>"JWT", "alg"=>"HS256"];
	$body = [
		"channel_id"=>"$userid",
		"exp"=>$expiry,
		"pubsub_perms"=>["send"=>["broadcast"]],
		"role"=>"external",
		"user_id"=>"$userid",
		"opaque_user_id"=>"U$userid",
	];

	$payload = urlsafeB64Encode(json_encode($header)) . "." .  urlsafeB64Encode(json_encode($body));

	$signature = hash_hmac("SHA256", $payload, base64_decode($ext_secret), true);
	$jwt = $payload . "." . urlsafeB64Encode($signature);

	return ['token'=>$jwt, 'expiry'=>$expiry];
}

main();
