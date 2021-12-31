import React from 'react';
import parse from 'html-react-parser';

import './Result.css';

export default function Result(props) {
    
    console.log(`result prop = ${JSON.stringify(props)}`)
    
    return(
    <div className="card result">
        <div className="card-body">
            <h5 className="title-style">
                <a href={`/details/${props.document.id}`}>
                {props.document.metadata_storage_name}
                </a>
            </h5>
            <h6 className="card-text">Search Score: {props.score.toLocaleString()}</h6>
            <h6 className="card-text">{props.document.keyPhrases?.join(' | ')}</h6>
            <p dangerouslysetInnerHTML={props.highlights.merged_text}/>
        </div>
    </div>
    );
}
