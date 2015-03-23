var DropdownButton = ReactBootstrap.DropdownButton;
var MenuItem = ReactBootstrap.MenuItem;
var Navbar = ReactBootstrap.Navbar;
var Nav = ReactBootstrap.Nav;
var NavItem = ReactBootstrap.NavItem;
var Modal = ReactBootstrap.Modal;
var ModalTrigger = ReactBootstrap.ModalTrigger;
var Button = ReactBootstrap.Button;
var Glyphicon = ReactBootstrap.Glyphicon;
var Input = ReactBootstrap.Input;
var Label = ReactBootstrap.Label;

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

var AddDeviceModal = React.createClass({
  loadRemote: function () {
     $.ajax({
         url: this.props.url,
         dataType: 'json',
         success: function (data) {
             this.setState({data: data[this.props.dataKey]});
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
  render: function() {
    return (
      <div>
        <Modal {...this.props} bsStyle="primary" title="Modal heading" animation closeButton={true}>
          <div className="modal-body">
            <h4>Text in a modal</h4>
            <p>This is where we would see a list of devices....</p>
            </div>
          <div className="modal-footer">
            <Button onClick={this.props.onRequestHide}>Close</Button>
          </div>
        </Modal>
        </div>
      );
  }
});


var EditPersonsModal = React.createClass({
  loadRemote: function () {
     $.ajax({
         url: this.props.url,
         dataType: 'json',
         success: function (data) {
             this.setState({data: data[this.props.dataKey]});
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
  render: function() {
    return (
      <div>
        <Modal {...this.props} bsStyle="primary" title="Edit People" animation closeButton={true}>
          <div className="modal-body">
              <PersonBox data={this.state.data} />
          </div>
          <div className="modal-footer">
            <Button onClick={this.props.onRequestHide}>Close</Button>
          </div>

        </Modal>
        </div>
      );
  }
});

var SelectPersonForm = React.createClass({
  nextStep: function (e) {
    e.preventDefault()
    var data = "userid blah"
    this.props.saveUserId(data)
    this.props.nextStep()
  },
  handleChange: function (e) {
    console.log('YEY');
    console.log(e);
  },
  render: function () {
    var inputNodes = this.props.data.map(function (d, index) {
      return(
        <Input type="radio" label={d.name} name="person" value={d.id} onClick={this.handleChange}/>
      );
    });
    return (
      <div className="person-select">
          <h4>Select a Person </h4>
          <form>
              {inputNodes}
              <Button type="submit" className="pull-right" onClick={this.nextStep}>
                  Select User.
              </Button>
          </form>
      </div>
    );
  }
});

var PersonBox = React.createClass({
  getInitialState: function() {
    return (
      {
        step: 1
      }
    );
  },
  saveUserId: function (data) {
    this.setState({
      userId: data
    })
  },
  nextStep: function() {
    this.setState({
      step: this.state.step + 1
    });
  },
  previousStep: function() {
    this.setState({
      step: this.state.step - 1
    });
  },
  render: function() {
    var step;
    switch(this.state.step) {
      case 1:
        return (
          <SelectPersonForm {...this.props}
                            nextStep={this.nextStep}
                            saveUserId={this.saveUserId} />
        );
      case 2:
        return (
          <div>
               {this.state.userId}
               <Glyphicon glyph="star" />
          </div>
        );
    }
    return (
      step
    );
  }
});

var BootstrapNav = React.createClass({
    render: function () {
        return (
          <Navbar className="fluid" brand={this.props.brand}>
              <Nav right>
                  <DropdownButton eventKey={1} title="Settings">
                      <ModalTrigger modal={<AddDeviceModal url='/api/devices/nearby' pollInterval={5000} dataKey='nearby_devices' />}>
                          <MenuItem eventKey="2">
                              <span>
                                  Add a Device
                                  <Glyphicon className="pull-right" glyph="plus"/>
                              </span>
                          </MenuItem>
                      </ModalTrigger>
                      <MenuItem divider />
                      <ModalTrigger modal={<EditPersonsModal url='/api/persons' pollInterval={3000} dataKey='persons' />}>
                          <MenuItem eventKey="3">
                              <span>
                                  Edit Users
                                  <Glyphicon className="pull-right" glyph="wrench"/>
                              </span>
                          </MenuItem>
                      </ModalTrigger>
                  </DropdownButton>
              </Nav>
          </Navbar>
        );
    }
});

  React.render(
      <AppContainer />,
      document.getElementById('content')
  );
