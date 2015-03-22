var AppContainer = React.createClass({
    render: function () {
        return (
            <div>
                <BootstrapNav brand="in" />
                <div className="container-fluid inApp">
                    <div className="row">
                        <div className="col-md-6 col-md-offset-3">
                            <PeopleBox url="/api/in" pollInterval={50}/>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

var PeopleBox = React.createClass({
     loadRemote: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            success: function (data) {
                this.setState({data: data['status']});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function () {
        return (
        {
            data: []
        }
        );
    },
    componentDidMount: function () {
        this.loadRemote();
        setInterval(this.loadRemote, this.props.pollInterval);
    },
    render: function () {
        return (
            <PersonList data={this.state.data}/>
        );
    }
});

var PersonList = React.createClass({
    render: function () {
        var personNodes = this.props.data.map(function (data) {
            return (
                <Person person={data}>
                    {data}
                </Person>
            );
        });
        return (
            <div className="personList">
                {personNodes}
            </div>
        );
    }
});

var Person = React.createClass({
    render: function () {
        return (
                <div className="person">
                    <BootstrapPersonPanel title={this.props.children.name}>
                        {this.props.children}
                    </BootstrapPersonPanel>
                </div>
        );
    }
});

var BootstrapPersonPanel = React.createClass({
    render: function () {
        Array.prototype.diff = function(a) {
            return this.filter(function(i) {return a.indexOf(i) < 0;});
        };

        var filterKeys = ['id'];

        var data = this.props.children;
        var propsAvailable = Object.keys(data);
        var propsSelected = propsAvailable.diff(filterKeys);

        var items = propsSelected.map(function(key) {
            var val = data[key];
            if (typeof(val) == "boolean") {
                val = val.toString();
            }
            if(val) {
                return (
                    <li>{key}:  {val}</li>        
                );
            }
        });
        var cx = React.addons.classSet;
        var classes = cx(
            {
                'panel panel-warning': !this.props.children.in,
                'panel panel-success': this.props.children.in
            }
        );

        return (
          <div className={classes}> 
              <div className="panel-heading"> {this.props.title} </div>
              <div className="panel-body">
                  <ul>
                      {items}
                  </ul>
              </div>
          </div>
        );
    }
});

var BootstrapNav = React.createClass({
    render: function () {
        return (
            <div className="nav navbar navbar-default">
                <div className="container-fluid">
                    <div className="navbar-header">
                        <a className="navbar-brand">
                          {this.props.brand}
                        </a>
                    </div>
                </div>
            </div>
        );
    }
});

React.render(
    <AppContainer />,
    document.getElementById('content')
);
