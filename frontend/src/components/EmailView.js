import React from 'react';
import utf8 from 'utf8';
import quotedPrintable from 'quoted-printable';

class EmailView extends React.Component {

  constructor(props) {
    super(props);
    this.state = {listOfHtml : [],
    html : '',
    curr_index : 0};
    this.fetchData = this.fetchData.bind(this);
    this.moveNext = this.moveNext.bind(this);
  }

  componentDidMount(){
   this.fetchData()
 }

 fetchData() {
   let str = '';
   let newList = [];
   fetch("http://localhost:4444/api/emails/search?fromAddress=<no-reply@sns.amazonaws.com>&numOfEmails=5")
   .then((resp) => {
    return resp.json();
    })
    .then((data) => {
      for (let email in data) {
        console.log(email);
        console.log(data[email]);
        if (data[email].quotable_printable !== undefined) {
            str = quotedPrintable.decode(data[email].quotable_printable);
            str = utf8.decode(str);
            str = str.split('</html>')[0];
            if (str.includes('<html lang="en">')) {
                str = str.split('<html lang="en">')[1];
            } else if (str.includes('<html>')) {
              str = str.split('<html>')[1];
            } else {
              str = str;
            }
            console.log(str);
        }
        else {
          str = data[email].text_plain;
        }
        newList.push(str);
    }
    this.setState({ listOfHtml: newList , html: newList[this.state.curr_index]});
    console.log(newList);
      //str = str.split('<html')
  });
  //  if (event) {
  //    this.setState({listOfHtml : ['1']});
  //    console.log('HERE123');
  // }
 }

  moveNext() {
    console.log('here');
    console.log(this.state.curr_index);
    let next_index = this.state.curr_index + 1
    if (next_index < this.state.listOfHtml.length) {
      this.setState({html : this.state.listOfHtml[next_index],
        curr_index: next_index});
    }
  }

  render() {
    return (
      <div>
        <div dangerouslySetInnerHTML={{__html:this.state.html}}></div>
        <button onClick={this.moveNext}>Next</button>
      </div>
    );
  }
}

export default EmailView;
