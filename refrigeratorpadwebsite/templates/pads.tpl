<html>
<body>
<a href="/">
	<div style="width:200px;height:50px;background-color:white;border:2px solid black;text-align:center">
		<br>
		<p style="margin:auto"> <b>Back to Main Menu</b></p>
	</div>
</a>
<h3> Pad Page </h3>
%for pad in '1234':
	<p><b>Pad {{pad}}: {{data[pad]}} </b> </p>
	<form action="/pads">
		put on pad {{pad}}: <input type="text" name="item{{pad}}" value=""> <br>
		<input type="submit" value="SUBMIT"> <br>
	</form>
%end
<p> Previously used items: </p>
%for history in history_data:
	<p> {{history}} </p>
%end
</body>
</html>