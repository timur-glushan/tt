/*
 * DATE EXTENSION - CALCULATING AND SETTING PERIODS
 *
 * *** All methods are using the client's local timezone!
 * Defines a set of functions to get midnight dates for nearest days, or by a given offset of days/months
*/

/*
 * Create a new Date object and set it to point on yesteday midnight.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateLastDate = function(dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(dateObject.getTime()-(24*60*60*1000));
	// dummy summer-time offset protection
	if (newDateObject.getDate() == dateObject.getDate()) {
		newDateObject = new Date(dateObject.getTime()-(30*60*60*1000));
	}
	newDateObject.setHours(0,0,0,0);
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on yesteday midnight.
*/
Date.prototype.setLastDate = function(){
	this.setTime( this.calculateLastDate().getTime() );
	return this;
}

/*
 * Create a new Date object and set it to point on today's midnight.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateLastMidnight = function(dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(this.getTime());
	newDateObject.setHours(0,0,0,0);
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on today's midnight.
*/
Date.prototype.setLastMidnight = function(){
	this.setTime( this.calculateLastMidnight().getTime() );
	return this;
}

/*
 * Create a new Date object and set it to point on tomorrow midnight.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateNextMidnight = function(dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(dateObject.getTime()+(24*60*60*1000));
	// dummy summer-time offset protection
	if (newDateObject.getDate() == dateObject.getDate()) {
		newDateObject = new Date(dateObject.getTime()+(30*60*60*1000));
	}
	newDateObject.setHours(0,0,0,0);
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on tomorrow midnight
*/
Date.prototype.setNextMidnight = function(){
	this.setTime( this.calculateNextMidnight().getTime() );
	return this;
}

/*
 * Create a new Date object and set it to point on midnight occured N days ago.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateDaysBack = function(days, dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(dateObject.getTime());
	newDateObject.setLastMidnight();
	for (var i=0; i<days; i++){
		newDateObject.setLastDate();
	}
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on midnight occured N days ago.
*/
Date.prototype.setDaysBack = function(days){
	this.setTime( this.calculateDaysBack(days).getTime() );
	return this;
}

/*
 * Create a new Date object and set it to point on midnight that will occur in N days.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateDaysForward = function(days, dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(dateObject.getTime());
	newDateObject.setLastMidnight();
	for (var i=0; i<days; i++){
		newDateObject.setNextMidnight();
	}
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on midnight that will occur in N days.
*/
Date.prototype.setDaysForward = function(days){
	this.setTime( this.calculateDaysForward(days).getTime() );
	return this;
}

/*
 * Create a new Date object and set it to point on midnight occured N months ago.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateMonthsBack = function(months, dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(dateObject.getTime());
	newDateObject.setLastMidnight();
	for (var i=0; i<months; i++){
		if (newDateObject.getMonth()==0){
			newDateObject.setFullYear(newDateObject.getFullYear()-1);
			newDateObject.setMonth(11);
		} else {
			newDateObject.setMonth(newDateObject.getMonth()-1);
		}
	}
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on midnight occured N months ago.
*/
Date.prototype.setMonthsBack = function(months){
	this.setTime( this.calculateMonthsBack(months).getTime() );
	return this;
}

/*
 * Create a new Date object and set it to point on midnight that will occur in N months.
 * Current Date object (this) is not affected.
*/
Date.prototype.calculateMonthsForward = function(months, dateObject){
	var dateObject = dateObject || this;
	var newDateObject = new Date(dateObject.getTime());
	newDateObject.setLastMidnight();
	for (var i=0; i<months; i++){
		if (newDateObject.getMonth()==11){
			newDateObject.setFullYear(newDateObject.getFullYear()+1);
			newDateObject.setMonth(0);
		} else {
			newDateObject.setMonth(newDateObject.getMonth()+1);
		}
	}
	return newDateObject;
}

/*
 * Set the current Date object (this) to point on midnight that will occur in N months.
*/
Date.prototype.setMonthsForward = function(months){
	this.setTime( this.calculateMonthsForward(months).getTime() );
	return this;
}
