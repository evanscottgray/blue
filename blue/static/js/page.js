var AppContainer = React.createClass({
    render: function () {
        return (
            <div>
                <BootstrapNav brand="in" />
                <PeopleBox url="/api/in" pollInterval={3000}/>
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
                console.log(data);
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
        var createPerson = function(person) {
            return  (<li>{person.name} - in: {person.in.toString()}</li>);
        };
        return (
            <div>
            <ul>{this.state.data.map(createPerson)}</ul>
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
