<html>
<body>
<a href="/">
	<div style="width:200px;height:50px;background-color:white;border:2px solid black;text-align:center">
		<br>
		<p style="margin:auto"> <b>Back to Main Menu</b></p>
	</div>
</a>		
<h3> Grocery List </h3>
%if len(data)>0:
	<form action="/grocery_list">
	%for i in data:
		<p>
			<b> {{i}} </b> 
				<input type="checkbox" name="delete" value="{{i}}"> Remove
		</p>
	%end
	<input type="submit" value="Save Changes">
%else:
	<b> Your grocery list is empty. </b>
%end
</form>
</body>
</html>