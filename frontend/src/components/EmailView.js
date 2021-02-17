import React from 'react';
import utf8 from 'utf8';
import quotedPrintable from 'quoted-printable';
import {
  encode, decode, trim,
  isBase64, isUrlSafeBase64
} from 'url-safe-base64'

class EmailView extends React.Component {

  constructor(props) {
    super(props);
    this.state = {listOfHtml : [],
    html : '',
    emailList: [],
    commonHeadersList: [],
    curr_index : 0,
    nextPageToken : ''}
    this.moveNext = this.moveNext.bind(this);
    this.fetchDataV2 = this.fetchDataV2.bind(this)
    this.selectEmail = this.selectEmail.bind(this);
  }

  componentDidMount(){
   this.fetchDataV2();
   let referenceToThis = this;
   let interval = setInterval(function(){
     // method to be executed;
      if (referenceToThis.state.nextPageToken !== 'NULL') {
        referenceToThis.moveNext();
      }
    }, 3000);
  }

 fetchData() {
   let str = '';
   let newList = [];
   fetch("http://localhost:4444/api/v1/emails/search?fromAddress=<no-reply@sns.amazonaws.com>&numOfEmails=50")
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
            if (str.includes('Content-Transfer-Encoding: base64')){
              str = str.split('Content-Transfer-Encoding: base64')[1];
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
  });
}

 fetchDataV2() {
   let str = '';
   let newList = [];
   fetch("http://localhost:4444/api/v2/emails/search?fromAddress=no-reply@sns.amazonaws.com&numOfEmails=15")
   .then((resp) => {
    return resp.json();
    })
    .then((data) => {
      this.setStateVariables(data);
    }).catch(error => {
      this.setState({'nextPageToken' : 'NULL'});
    });
  }


  setStateVariables(data) {
    let currNextPageToken = data.pageToken;
    data = data.emails;
    let currEmailList = this.state.emailList;
    let currCommonHeadersList = this.state.commonHeadersList;
    for (let i in data) {
      let awsData = trim(data[i]['payload']['body']['data'] + '==');
      let urlSafeBase64AwsData = decode(awsData);
      let base64decodedAwsData = atob(urlSafeBase64AwsData);
      if (encodeURI(base64decodedAwsData).substring(0,30) === '%7B%0D%0A%20%20%22Type%22%20:%') {
        let utf8decodedAwsData = decode(base64decodedAwsData);
        if (!JSON.parse(utf8decodedAwsData)['Message'].startsWith('{')) continue;
        let jsonParsedEmail = JSON.parse(JSON.parse(utf8decodedAwsData)['Message']);
        currEmailList.push(jsonParsedEmail);
        jsonParsedEmail['mail']['commonHeaders']['messageId'] = jsonParsedEmail['mail']['commonHeaders']['messageId']+ (this.state.commonHeadersList.length + i + 1);
        currCommonHeadersList.push(jsonParsedEmail['mail']['commonHeaders']);
        }
      }
      this.setState({
        emailList: currEmailList,
        commonHeadersList : currCommonHeadersList,
        nextPageToken : currNextPageToken});
      console.log(currEmailList);
      console.log(this.state.commonHeadersList);
  }

  moveNext() {
    let str = '';
    let newList = [];
    let isEnd = false;
    fetch("http://localhost:4444/api/v2/emails/search?fromAddress=no-reply@\
      sns.amazonaws.com&numOfEmails=15&pageToken="+this.state.nextPageToken)
    .then((resp) => {
     return resp.json();
     })
     .then((data) => {
       this.setStateVariables(data);
     }).catch((error) => {
       isEnd = true;
     });
    }

  selectEmail(event) {
      let currEmailList = this.state.emailList[parseInt(event.target.name)];
      this.setState({html : JSON.stringify(currEmailList)});
      console.log(this.state.html);
    }

//<div dangerouslySetInnerHTML={{__html:this.state.html}}></div>
// {this.state.commonHeadersList.length > 0 && this.state.commonHeadersList.map((value, index) => {
// return <li key={index}>{value}</li>
// })}

  render() {
    const insertableHTML = decode(this.state.html)
    const commonHeadersList = this.state.commonHeadersList.map((header, index) =>
      <div>
        <button className="listItem"
                name={index}
                key={header.messageId}
                onClick={this.selectEmail}>{decode(header.from[0].replace(/[<>]/g,''))}
        </button>
      </div>
    );
    return (
      <div>
        <button onClick={this.moveNext}>Next</button>
        {commonHeadersList}
        <div dangerouslySetInnerHTML={{__html:insertableHTML}}></div>
        <div>
        {this.state.nextPageToken !== 'NULL' ? 'Loading More...' : ''}
        </div>
      </div>
    );
  }
}

export default EmailView;
